# Copyright 2019 The resource-policy-evaluation-library Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from urllib.parse import urlparse
from .base import Resource
from rpe.exceptions import is_retryable_exception
from rpe.exceptions import UnsupportedRemediationSpec
from rpe.exceptions import InvalidRemediationSpecStep
import tenacity
from googleapiclienthelpers.discovery import build_subresource
from googleapiclienthelpers.waiter import Waiter


class GoogleAPIResource(Resource):

    # Names of the get and update methods. Most are the same but override in
    # the Resource if necessary
    resource_property = None
    get_method = "get"
    update_method = "update"

    # If a resource is not in a ready state, we can't update it. If we retrieve
    # it, and the state changes, updates will be rejected because the ETAG will
    # have changed. If a resource defines readiness criteria, the get() call
    # will wait until the resource is in a ready state to return
    #
    # Key/Value to check to see if a resource is ready
    readiness_key = None
    readiness_value = None

    def __init__(self, resource_data, **kwargs):
        full_resource_path = "{}.{}".format(
            self.service_name,
            self.resource_path
        )

        self.service = build_subresource(
            full_resource_path,
            self.version,
            **kwargs
        )

        # Support original update method until we can deprecate it
        self.update = self.remediate

        # If we are a property of a resource, also get the resource we're
        # associated with
        if self.is_property():
            # Build resource data for the parent
            parent_data = resource_data.copy()
            parent_type = resource_data['resource_type'].rsplit('.', 1)[0]
            parent_data['resource_type'] = parent_type

            self.parent_resource = GoogleAPIResource.factory(
                parent_data,
                **kwargs
            )

        self.resource_data = resource_data

    def is_property(self):
        return self.resource_property is not None

    @staticmethod
    def factory(resource_data, **kargs):
        resource_type_map = {
            'apps.services.versions.instances': GcpAppEngineInstance,
            'bigquery.datasets': GcpBigqueryDataset,
            'cloudfunctions.projects.locations.functions': GcpCloudFunction,
            'cloudfunctions.projects.locations.functions.iam': GcpCloudFunctionIam,
            'compute.instances': GcpComputeInstance,
            'compute.disks': GcpComputeDisks,
            'compute.subnetworks': GcpComputeSubnetwork,
            'compute.firewalls': GcpComputeFirewall,
            'container.projects.locations.clusters': GcpGkeCluster,
            'container.projects.locations.clusters.nodePools': GcpGkeClusterNodepool,
            'cloudresourcemanager.projects': GcpProject,
            'cloudresourcemanager.projects.iam': GcpProjectIam,
            'dataproc.clusters': GcpDataprocCluster,
            'pubsub.projects.subscriptions': GcpPubsubSubscription,
            'pubsub.projects.subscriptions.iam': GcpPubsubSubscriptionIam,
            'pubsub.projects.topics': GcpPubsubTopic,
            'pubsub.projects.topics.iam': GcpPubsubTopicIam,
            'serviceusage.services': GcpProjectService,
            'sqladmin.instances': GcpSqlInstance,
            'storage.buckets': GcpStorageBucket,
            'storage.buckets.iam': GcpStorageBucketIamPolicy
        }

        resource_type = resource_data.get('resource_type')
        if not resource_type:
            assert 0, 'Unrecognized resource'

        if resource_type not in resource_type_map:
            assert 0, 'Unrecognized resource'

        cls = resource_type_map.get(resource_type)
        return cls(resource_data, **kargs)

    def type(self):
        type_components = ["gcp", self.service_name, self.resource_path]

        # Things like IAM policy are not separate resources, but rather
        # properties of a resource. We may want to evaluate policy on these
        # properties, so we represent them as resources and need to distinguish
        # them in the resource type.
        if self.is_property():
            type_components.append(self.resource_property)

        return ".".join(type_components)

    # Google's documentation describes what it calls a 'full resource name' for
    # resources. None of the API's seem to implement it (except Cloud Asset
    # Inventory). This attempts to generate it from the discovery-based api
    # client's generated http request url.
    #
    # If we inject it into the resource, we can use it in policy evaluation to
    # simplify the structure of our policies
    def full_resource_name(self):

        # If this is a resource property, return the resource's frn instead
        if self.is_property():
            return self.parent_resource.full_resource_name()

        method = getattr(self.service, self.get_method)
        uri = method(**self._get_request_args()).uri

        uri_parsed = urlparse(uri)
        domain = uri_parsed.netloc
        path_segments = uri_parsed.path[1:].split('/')

        # First we need the name of the api
        if domain.startswith("www."):
            # we need to get the api name from the path
            api_name = path_segments.pop(0)
        else:
            # the api name is the first segment of the domain
            api_name = domain.split('.')[0]

            # occasionally the compute api baseUrl is returned as
            # compute.googleapis.com/compute, in which case we need to remove
            # the duplicated api reference
            if api_name == path_segments[0]:
                path_segments.pop(0)

        # Remove the version from the path
        path_segments.pop(0)

        # Remove method from the last path segment
        if ":" in path_segments[-1]:
            path_segments[-1] = path_segments[-1].split(":")[0]

        # Annoying resource-specific fixes
        if api_name == 'storage' and path_segments[0] == 'b':
            path_segments[0] = "buckets"

        resource_path = "/".join(path_segments)

        return "//{}.googleapis.com/{}".format(api_name, resource_path)

    def get(self):
        method = getattr(self.service, self.get_method)

        # If the resource has readiness criteria, wait for it
        if self.readiness_key and self.readiness_value:
            waiter = Waiter(method, **self._get_request_args())
            asset = waiter.wait(
                self.readiness_key,
                self.readiness_value,
                interval=10,
                retries=60
            )
        else:
            asset = method(**self._get_request_args()).execute()

        asset['_full_resource_name'] = self.full_resource_name()

        # if this asset is a property, inject its parent
        if self.is_property():
            parent = self.parent_resource.get()
            asset['_resource'] = parent
        return asset

    # Determine what remediation steps to take, fall back to the original resource-defined update method
    def remediate(self, remediation):
        # Check for an update spec version, default to version 1
        remediation_spec = remediation.get('_remediation_spec', "v1")
        if remediation_spec == "v1":

            # If no remediation_spec is listed, fall back to previous behavior
            # We inject the _full_resource_name in requests, so we need to remove it
            for key in list(remediation):
                if key.startswith('_'):
                    del remediation[key]

            method_name = self.update_method
            params = self._update_request_args(remediation)

            self._call_method(method_name, params)

        elif remediation_spec == "v2beta1":
            required_keys = ['method', 'params']

            for step in remediation.get('steps', []):
                if not all(k in step for k in required_keys):
                    raise InvalidRemediationSpecStep()

                method_name = step.get('method')
                params = step.get('params')
                self._call_method(method_name, params)
        else:
            raise UnsupportedRemediationSpec("The specified remediation spec is not supported")

    @tenacity.retry(
        retry=tenacity.retry_if_exception(is_retryable_exception),
        wait=tenacity.wait_random_exponential(multiplier=1, max=10),
        stop=tenacity.stop_after_attempt(10)
    )
    def _call_method(self, method_name, params):
        ''' Call the requested method on the resource '''
        method = getattr(self.service, method_name)
        return method(**params).execute()

class GcpAppEngineInstance(GoogleAPIResource):


    service_name = "appengine"
    resource_path = "apps.services.versions.instances"
    version = "v1"
    update_method = "debug"

    def _get_request_args(self):
        return {
            'appsId': self.resource_data['resource_name'].split('/')[1],
            'servicesId': self.resource_data['resource_name'].split('/')[3],
            'versionsId': self.resource_data['resource_name'].split('/')[5],
            'instancesId': self.resource_data['resource_name'].split('/')[-1]
        }

    def _update_request_args(self, body):
        return {
            'appsId': self.resource_data['resource_name'].split('/')[1],
            'servicesId': self.resource_data['resource_name'].split('/')[3],
            'versionsId': self.resource_data['resource_name'].split('/')[5],
            'instancesId': self.resource_data['resource_name'].split('/')[-1]
        }


class GcpBigqueryDataset(GoogleAPIResource):

    service_name = "bigquery"
    resource_path = "datasets"
    version = "v2"

    def _get_request_args(self):
        return {
            'datasetId': self.resource_data['resource_name'],
            'projectId': self.resource_data['project_id']
        }

    def _update_request_args(self, body):
        return {
            'datasetId': self.resource_data['resource_name'],
            'projectId': self.resource_data['project_id'],
            'body': body
        }


class GcpCloudFunction(GoogleAPIResource):

    service_name = "cloudfunctions"
    resource_path = "projects.locations.functions"
    version = "v1"
    update_method = "patch"

    def _get_request_args(self):
        return {
            'name': 'projects/{}/locations/{}/functions/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_location'],
                self.resource_data['resource_name']
            ),
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/locations/{}/functions/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_location'],
                self.resource_data['resource_name']
            ),
            'body': body
        }


class GcpCloudFunctionIam(GcpCloudFunction):

    resource_property = 'iam'
    get_method = "getIamPolicy"
    update_method = "setIamPolicy"

    def _get_request_args(self):
        return {
            'resource': 'projects/{}/locations/{}/functions/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_location'],
                self.resource_data['resource_name']
            ),
        }

    def _update_request_args(self, body):
        return {
            'resource': 'projects/{}/locations/{}/functions/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_location'],
                self.resource_data['resource_name']
            ),
            'body': {
                'policy': body
            }
        }


class GcpComputeInstance(GoogleAPIResource):

    service_name = "compute"
    resource_path = "instances"
    version = "v1"

    def _get_request_args(self):
        return {
            'instance': self.resource_data['resource_name'],
            'zone': self.resource_data['resource_location'],
            'project': self.resource_data['project_id']
        }

    def _update_request_args(self, body):
        return {
            'instance': self.resource_data['resource_name'],
            'zone': self.resource_data['resource_location'],
            'project': self.resource_data['project_id']
        }

class GcpComputeDisks(GoogleAPIResource):

    service_name = "compute"
    resource_path = "disks"
    version = "v1"

    def _get_request_args(self):
        return {
            'project': self.resource_data['project_id'],
            'zone': self.resource_data['resource_location'],
            'disk': self.resource_data['resource_name']
        }

    def _update_request_args(self, body):
        return {
            'project': self.resource_data['project_id'],
            'zone': self.resource_data['resource_location'],
            'disk': self.resource_data['resource_name']
        }

class GcpComputeSubnetwork(GoogleAPIResource):

    service_name = "compute"
    resource_path = "subnetworks"
    version = "v1"
    update_method = "patch"

    def _get_request_args(self):
        return {
            'project': self.resource_data['project_id'],
            'region': self.resource_data['resource_location'],
            'subnetwork': self.resource_data['resource_name']
        }

    def _update_request_args(self, body):
        return {
            'project': self.resource_data['project_id'],
            'region': self.resource_data['resource_location'],
            'subnetwork': self.resource_data['resource_name'],
            'body': body
        }


class GcpComputeFirewall(GoogleAPIResource):

    service_name = "compute"
    resource_path = "firewalls"
    version = "v1"
    update_method = "patch"

    def _get_request_args(self):
        return {
            'firewall': self.resource_data['resource_name'],
            'project': self.resource_data['project_id']
        }

    def _update_request_args(self, body):
        return {
            'firewall': self.resource_data['resource_name'],
            'project': self.resource_data['project_id'],
            'body': body
        }


class GcpDataprocCluster(GoogleAPIResource):
    service_name = "dataproc"
    resource_path = "projects.regions.clusters"
    update_method = "patch"
    version = "v1beta2"

    def _get_request_args(self):
        return {
            'projectId': self.resource_data['project_id'],
            'region': self.resource_data['resource_location'],
            'clusterName': self.resource_data['resource_name']
        }

    def _update_request_args(self, body):
        return {
            'projectId': self.resource_data['project_id'],
            'region': self.resource_data['resource_location'],
            'clusterName': self.resource_data['resource_name']
        }


      
class GcpGkeCluster(GoogleAPIResource):

    service_name = "container"
    resource_path = "projects.locations.clusters"
    version = "v1"
    readiness_key = 'status'
    readiness_value = 'RUNNING'

    def _get_request_args(self):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_location'],
                self.resource_data['resource_name']
            )
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_location'],
                self.resource_data['resource_name']
            ),
            'body': body
        }


class GcpGkeClusterNodepool(GoogleAPIResource):

    service_name = "container"
    resource_path = "projects.locations.clusters.nodePools"
    version = "v1"
    readiness_key = 'status'
    readiness_value = 'RUNNING'

    def _get_request_args(self):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_location'],
                self.resource_data['resource_name']
            )
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_location'],
                self.resource_data['resource_name']
            ),
            'body': body
        }


class GcpPubsubSubscription(GoogleAPIResource):

    service_name = "pubsub"
    resource_path = "projects.subscriptions"
    version = "v1"
    update_method = "patch"

    def _get_request_args(self):
        return {
            'subscription': 'projects/{}/subscriptions/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_name']
            )
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/subscriptions/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_name']
            ),
            'body': {
                'subscription': body,
                'updateMask': 'labels,ack_deadline_seconds,push_config,message_retention_duration,retain_acked_messages,expiration_policy'
            }
        }


class GcpPubsubSubscriptionIam(GcpPubsubSubscription):

    resource_property = 'iam'
    get_method = "getIamPolicy"
    update_method = "setIamPolicy"

    def _get_request_args(self):
        return {
            'resource': 'projects/{}/subscriptions/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_name']
            )
        }

    def _update_request_args(self, body):
        return {
            'resource': 'projects/{}/subscriptions/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_name']
            ),
            'body': {
                'policy': body
            }
        }


class GcpPubsubTopic(GoogleAPIResource):

    service_name = "pubsub"
    resource_path = "projects.topics"
    version = "v1"
    update_method = "patch"

    def _get_request_args(self):
        return {
            'topic': 'projects/{}/topics/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_name']
            )
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/topics/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_name']
            ),
            'body': {
                'topic': body,
                # the name field is immutable
                'updateMask': 'labels'
            }
        }


class GcpPubsubTopicIam(GcpPubsubTopic):

    resource_property = "iam"
    get_method = "getIamPolicy"
    update_method = "setIamPolicy"

    def _get_request_args(self):
        return {
            'resource': 'projects/{}/topics/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_name']
            )
        }

    def _update_request_args(self, body):
        return {
            'resource': 'projects/{}/topics/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_name']
            ),
            'body': {
                'policy': body
            }
        }

class GcpStorageBucket(GoogleAPIResource):

    service_name = "storage"
    resource_path = "buckets"
    version = "v1"

    def _get_request_args(self):
        return {
            'bucket': self.resource_data['resource_name'],
            'userProject': self.resource_data['project_id']
        }

    def _update_request_args(self, body):
        return {
            'bucket': self.resource_data['resource_name'],
            'userProject': self.resource_data['project_id'],
            'body': body
        }


class GcpStorageBucketIamPolicy(GcpStorageBucket):

    resource_property = "iam"
    get_method = "getIamPolicy"
    update_method = "setIamPolicy"


class GcpSqlInstance(GoogleAPIResource):

    service_name = "sqladmin"
    resource_path = "instances"
    version = "v1beta4"
    readiness_key = 'state'
    readiness_value = 'RUNNABLE'

    def _get_request_args(self):
        return {
            'instance': self.resource_data['resource_name'],
            'project': self.resource_data['project_id']
        }

    def _update_request_args(self, body):
        return {
            'instance': self.resource_data['resource_name'],
            'project': self.resource_data['project_id'],
            'body': body
        }


class GcpProject(GoogleAPIResource):

    service_name = "cloudresourcemanager"
    resource_path = "projects"
    version = "v1"

    def _get_request_args(self):
        return {
            'projectId': self.resource_data['resource_name']
        }

    def _update_request_args(self, body):
        return {
            'projectId': self.resource_data['resource_name'],
            'body': body
        }


class GcpProjectIam(GcpProject):

    resource_property = "iam"
    get_method = "getIamPolicy"
    update_method = "setIamPolicy"

    def _get_request_args(self):
        return {
            'resource': self.resource_data['resource_name'],
            'body': {}
        }

    def _update_request_args(self, body):
        return {
            'resource': self.resource_data['resource_name'],
            'body': {
                'policy': body,
                'updateMask': "bindings,etag,auditConfigs"
            }
        }

class GcpProjectService(GoogleAPIResource):

    service_name = "serviceusage"
    resource_path = "services"
    version = "v1"

    def _get_request_args(self):
        return {
            'name': 'projects/{}/services/{}'.format(
                self.resource_data['project_id'],
                self.resource_data['resource_name']
            )
        }

    def _update_request_args(self, body):
        raise NotImplementedError("Update request not available")