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


import re
from urllib.parse import urlparse
from .base import Resource
from rpe.exceptions import is_retryable_exception
from rpe.exceptions import ResourceException
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
    required_resource_data = ['name']

    parent_cls = None

    # If a resource is not in a ready state, we can't update it. If we retrieve
    # it, and the state changes, updates will be rejected because the ETAG will
    # have changed. If a resource defines readiness criteria, the get() call
    # will wait until the resource is in a ready state to return
    #
    # Key/Value to check to see if a resource is ready
    readiness_key = None
    readiness_value = None

    def __init__(self, client_kwargs={}, **resource_data):

        # Set some defaults
        self._service = None
        self._parent_resource = None

        # Load and validate additional resource data
        self._resource_data = resource_data
        self._validate_resource_data()

        # Store the client kwargs to pass to any new clients
        self._client_kwargs = client_kwargs

        # Support original update method until we can deprecate it
        self.update = self.remediate

        self._ancestry = None

    def _validate_resource_data(self):
        ''' Verify we have all the required data for this resource '''
        if not all(arg in self._resource_data for arg in self.required_resource_data):

            raise ResourceException(
                'Missing data required for resource creation. Expected data: {}; Got: {}'.format(
                    ','.join(self.required_resource_data),
                    ','.join(self._resource_data.keys())
                )
            )

    def is_property(self):
        return self.resource_property is not None

    @staticmethod
    def _extract_cai_name_data(name):
        ''' Attempt to get identifiable information out of resource_name '''

        # Most resources need only a subset of these fields to query the google apis
        fields = {
            'project_id': r'/projects/([^\/]+)/',
            'location': r'/(?:locations|regions|zones)/([^\/]+)/',
            'name': r'([^\/]+)$',


            # Less-common resource data
            #  AppEngine
            'app': r'/apps/([^\/]+)/',
            'service': r'/services/([^\/]+)/',
            'version': r'/versions/([^\/]+)/',

            #  NodePools
            'cluster': r'/clusters/([^\/]+)/',
        }

        resource_data = {}

        # Extract available resource data from resource name
        for field_name in fields:
            m = re.search(fields[field_name], name)
            if m:
                resource_data[field_name] = m.group(1)

        return resource_data

    @staticmethod
    def from_cai_data(resource_name, asset_type, content_type='resource', client_kwargs={}):

        # CAI classifies things by content_type (ex: resource or iam)
        # and asset_type (ex: storage bucket or container cluster)
        cai_map = {
            'resource': {

                # App Engine instances show up as compute instances in CAI exports. We've chosen to
                # define our own asset_type and do some munging outside of rpelib
                'appengine.googleapis.com/Instance': GcpAppEngineInstance,

                'bigquery.googleapis.com/Dataset': GcpBigqueryDataset,
                'bigtableadmin.googleapis.com/Instance': GcpBigtableInstance,

                # Cloudfunctions are not currently supported by CAI. We reached out to the CAI team
                # to find out what the asset_type would likely be
                'cloudfunctions.googleapis.com/CloudFunction': GcpCloudFunction,

                'compute.googleapis.com/Instance': GcpComputeInstance,
                'compute.googleapis.com/Disk': GcpComputeDisks,
                'compute.googleapis.com/Subnetwork': GcpComputeSubnetwork,
                'compute.googleapis.com/Firewall': GcpComputeFirewall,
                'dataproc.googleapis.com/Cluster': GcpDataprocCluster,
                'container.googleapis.com/Cluster': GcpGkeCluster,
                'container.googleapis.com/NodePool': GcpGkeClusterNodepool,
                'pubsub.googleapis.com/Subscription': GcpPubsubSubscription,
                'pubsub.googleapis.com/Topic': GcpPubsubTopic,
                'storage.googleapis.com/Bucket': GcpStorageBucket,
                'sqladmin.googleapis.com/Instance': GcpSqlInstance,
                'cloudresourcemanager.googleapis.com/Project': GcpProject,
                'serviceusage.googleapis.com/Service': GcpProjectService,
            },
            'iam': {
                "bigtableadmin.googleapis.com/Instance": GcpBigtableInstanceIam,
                "cloudfunctions.googleapis.com/CloudFunction": GcpCloudFunctionIam,
                "pubsub.googleapis.com/Subscription": GcpPubsubSubscriptionIam,
                "pubsub.googleapis.com/Topic": GcpPubsubTopicIam,
                "storage.googleapis.com/Bucket": GcpStorageBucketIamPolicy,
                "cloudresourcemanager.googleapis.com/Project": GcpProjectIam,
            }
        }

        if content_type not in cai_map:
            raise ResourceException('Unrecognized content type: {}'.format(content_type))

        asset_type_map = cai_map.get(content_type)

        if asset_type not in asset_type_map:
            raise ResourceException('Unrecognized asset type: {}'.format(asset_type))

        cls = asset_type_map.get(asset_type)

        resource_data = GoogleAPIResource._extract_cai_name_data(resource_name)

        return cls(
            client_kwargs=client_kwargs,
            **resource_data
        )

    @staticmethod
    def factory(client_kwargs={}, **kwargs):
        resource_type_map = {
            'apps.services.versions.instances': GcpAppEngineInstance,
            'bigquery.datasets': GcpBigqueryDataset,
            'bigtableadmin.projects.instances': GcpBigtableInstance,
            'bigtableadmin.projects.instances.iam': GcpBigtableInstanceIam,
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

        resource_type = kwargs.get('resource_type')
        if not resource_type:
            raise ResourceException('Resource type not specified')

        if resource_type not in resource_type_map:
            raise ResourceException('Unknown resource type: {}'.format(resource_type))

        cls = resource_type_map.get(resource_type)
        return cls(client_kwargs=client_kwargs, **kwargs)

    def to_dict(self):
        details = self._resource_data.copy()
        details.update({
            'cai_type': self.cai_type,
            'full_resource_name': self.full_resource_name(),
            'organization': self.organization,
        })
        return details

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

        # CAI uses cloudsql.googleapis.com in their full_resource_name, so we need to detect all
        # bad incarnations and replace them
        bad_sql_names = ['sql', 'sqladmin']

        # First we need the name of the api
        if domain.startswith("www."):
            # we need to get the api name from the path
            api_name = path_segments.pop(0)
            api_name = 'cloudsql' if api_name in bad_sql_names else api_name
        else:
            # the api name is the first segment of the domain
            api_name = domain.split('.')[0]

            # the sql api is now returning sqladmin.googleapis.com/sql/<ver>
            # and the CAI docs state the FRN for sql instances should start
            # with //cloudsql.googleapis.com/ so lets replace all odd sql ones
            # and rely on the code below to catch duplicates
            path_segments[0] = 'cloudsql' if path_segments[0] in bad_sql_names else path_segments[0]
            api_name = 'cloudsql' if api_name in bad_sql_names else api_name

            # occasionally the compute api baseUrl is returned as
            # compute.googleapis.com/compute, in which case we need to remove
            # the duplicated api reference
            # also addresses the sql issue mentioned above
            if api_name == path_segments[0]:
                path_segments.pop(0)

        # Remove the version from the path
        path_segments.pop(0)

        # Remove method from the last path segment
        if ":" in path_segments[-1]:
            path_segments[-1] = path_segments[-1].split(":")[0]

        # Annoying resource-specific fixes

        # The url for buckets is `/b/` instead of `/buckets/`. Initially this fixed that
        # Unfortunately, CAI omits the collection name, rather than follow Google's API design doc
        # So we just remove the collection name
        #
        # https://cloud.google.com/apis/design/resource_names
        # See: https://issuetracker.google.com/issues/131586763
        #
        if api_name == 'storage' and path_segments[0] == 'b':
            path_segments.pop(0)
            # Replace with this if they fix CAI:
            # path_segments[0] = "buckets"

        if api_name == 'bigtableadmin':
            api_name = 'bigtable'

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
                retries=90
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
        wait=tenacity.wait_random_exponential(multiplier=5, max=20),
        stop=tenacity.stop_after_attempt(15)
    )
    def _call_method(self, method_name, params):
        ''' Call the requested method on the resource '''
        method = getattr(self.service, method_name)
        return method(**params).execute()

    @property
    def ancestry(self):
        if self._ancestry:
            return self._ancestry

        # attempt to fill in the resource's ancestry
        # if the target project has the cloudresourcemanager api disabled, this will fail
        # if the resource_data doesn't include the project_id (ex: with storage buckets) this will also fail
        try:
            resource_manager_projects = build_subresource(
                'cloudresourcemanager.projects', 'v1', **self._client_kwargs
            )

            resp = resource_manager_projects.getAncestry(
                projectId=self.project_id
            ).execute()

            # Reformat getAncestry response to be a list of resource names
            self._ancestry = [
                f"//cloudresourcemanager.googleapis.com/{ancestor['resourceId']['type']}s/{ancestor['resourceId']['id']}"
                for ancestor in resp.get('ancestor')
            ]

        except Exception:
            # This call is best-effort. Any failures should be caught
            pass

        return self._ancestry

    @property
    def organization(self):
        ancestry = self.ancestry
        if not ancestry:
            return None

        return next(
            (ancestor for ancestor in ancestry if ancestor.startswith('//cloudresourcemanager.googleapis.com/organizations/')),
            None
        )

    @property
    def client_kwargs(self):
        return self._client_kwargs

    @client_kwargs.setter
    def client_kwargs(self, client_kwargs):

        # Invalidate service/parent because client_kwargs changed
        self._service = None
        self._parent_resource = None

        self._client_kwargs = client_kwargs

    @property
    def service(self):
        if self._service is None:

            full_resource_path = "{}.{}".format(
                self.service_name,
                self.resource_path
            )

            self._service = build_subresource(
                full_resource_path,
                self.version,
                **self._client_kwargs
            )
        return self._service

    @property
    def project_id(self):
        return self._resource_data.get('project_id')

    @property
    def parent_resource(self):
        # If there is a parent class, return it as a resource

        if self._parent_resource is None and self.parent_cls:

            self._parent_resource = self.parent_cls(
                client_kwargs=self._client_kwargs,
                **self._resource_data.copy()
            )
        return self._parent_resource


class GcpAppEngineInstance(GoogleAPIResource):

    service_name = "appengine"
    resource_path = "apps.services.versions.instances"
    version = "v1"
    readiness_key = 'vmStatus'
    readiness_value = 'RUNNING'
    update_method = "debug"

    cai_type = 'appengine.googleapis.com/Instance'  # this is made-up based on existing appengine types

    required_resource_data = ['name', 'app', 'service', 'version']

    cai_type = None             # unknown

    def _get_request_args(self):
        return {
            'appsId': self._resource_data['app'],
            'servicesId': self._resource_data['service'],
            'versionsId': self._resource_data['version'],
            'instancesId': self._resource_data['name']
        }

    def _update_request_args(self, body):
        return {
            'appsId': self._resource_data['app'],
            'servicesId': self._resource_data['service'],
            'versionsId': self._resource_data['version'],
            'instancesId': self._resource_data['name']
        }


class GcpBigqueryDataset(GoogleAPIResource):

    service_name = "bigquery"
    resource_path = "datasets"
    version = "v2"

    required_resource_data = ['name', 'project_id']

    cai_type = "bigquery.googleapis.com/Dataset"

    def _get_request_args(self):
        return {
            'datasetId': self._resource_data['name'],
            'projectId': self._resource_data['project_id']
        }

    def _update_request_args(self, body):
        return {
            'datasetId': self._resource_data['name'],
            'projectId': self._resource_data['project_id'],
            'body': body
        }


class GcpBigtableInstance(GoogleAPIResource):

    service_name = "bigtableadmin"
    resource_path = "projects.instances"
    version = "v2"
    update_method = "partialUpdateInstance"
    readiness_key = 'state'
    readiness_value = 'READY'

    required_resource_data = ['name', 'project_id']

    cai_type = "bigtableadmin.googleapis.com/Instance"

    def _get_request_args(self):
        return {
            'name': 'projects/{}/instances/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            ),
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/instances/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            ),
            'body': body,
            'updateMask': 'labels,displayName,type'
        }


class GcpBigtableInstanceIam(GcpBigtableInstance):

    resource_property = 'iam'
    parent_cls = GcpBigtableInstance
    get_method = "getIamPolicy"
    update_method = "setIamPolicy"
    readiness_key = None
    readiness_value = None

    def _get_request_args(self):
        return {
            'resource': 'projects/{}/instances/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            ),
        }

    def _update_request_args(self, body):
        return {
            'resource': 'projects/{}/instances/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            ),
            'body': {
                'policy': body
            }
        }


class GcpCloudFunction(GoogleAPIResource):

    service_name = "cloudfunctions"
    resource_path = "projects.locations.functions"
    version = "v1"
    update_method = "patch"

    required_resource_data = ['name', 'location', 'project_id']

    cai_type = "cloudfunctions.googleapis.com/CloudFunction"  # unreleased

    def _get_request_args(self):
        return {
            'name': 'projects/{}/locations/{}/functions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['name']
            ),
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/locations/{}/functions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['name']
            ),
            'body': body
        }


class GcpCloudFunctionIam(GcpCloudFunction):

    resource_property = 'iam'
    parent_cls = GcpCloudFunction
    get_method = "getIamPolicy"
    update_method = "setIamPolicy"

    def _get_request_args(self):
        return {
            'resource': 'projects/{}/locations/{}/functions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['name']
            ),
        }

    def _update_request_args(self, body):
        return {
            'resource': 'projects/{}/locations/{}/functions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['name']
            ),
            'body': {
                'policy': body
            }
        }


class GcpComputeInstance(GoogleAPIResource):

    service_name = "compute"
    resource_path = "instances"
    version = "v1"

    required_resource_data = ['name', 'location', 'project_id']

    cai_type = "compute.googleapis.com/Instance"

    def _get_request_args(self):
        return {
            'instance': self._resource_data['name'],
            'zone': self._resource_data['location'],
            'project': self._resource_data['project_id']
        }

    def _update_request_args(self, body):
        return {
            'instance': self._resource_data['name'],
            'zone': self._resource_data['location'],
            'project': self._resource_data['project_id']
        }


class GcpComputeDisks(GoogleAPIResource):

    service_name = "compute"
    resource_path = "disks"
    version = "v1"

    required_resource_data = ['name', 'location', 'project_id']

    cai_type = "compute.googleapis.com/Disk"

    def _get_request_args(self):
        return {
            'project': self._resource_data['project_id'],
            'zone': self._resource_data['location'],
            'disk': self._resource_data['name']
        }

    def _update_request_args(self, body):
        return {
            'project': self._resource_data['project_id'],
            'zone': self._resource_data['location'],
            'disk': self._resource_data['name']
        }


class GcpComputeSubnetwork(GoogleAPIResource):

    service_name = "compute"
    resource_path = "subnetworks"
    version = "v1"
    update_method = "patch"

    required_resource_data = ['name', 'location', 'project_id']

    cai_type = "compute.googleapis.com/Subnetwork"

    def _get_request_args(self):
        return {
            'project': self._resource_data['project_id'],
            'region': self._resource_data['location'],
            'subnetwork': self._resource_data['name']
        }

    def _update_request_args(self, body):
        return {
            'project': self._resource_data['project_id'],
            'region': self._resource_data['location'],
            'subnetwork': self._resource_data['name'],
            'body': body
        }


class GcpComputeFirewall(GoogleAPIResource):

    service_name = "compute"
    resource_path = "firewalls"
    version = "v1"
    update_method = "patch"

    required_resource_data = ['name', 'project_id']

    cai_type = "compute.googleapis.com/Firewall"

    def _get_request_args(self):
        return {
            'firewall': self._resource_data['name'],
            'project': self._resource_data['project_id']
        }

    def _update_request_args(self, body):
        return {
            'firewall': self._resource_data['name'],
            'project': self._resource_data['project_id'],
            'body': body
        }


class GcpDataprocCluster(GoogleAPIResource):
    service_name = "dataproc"
    resource_path = "projects.regions.clusters"
    update_method = "patch"
    version = "v1beta2"

    required_resource_data = ['name', 'location', 'project_id']

    cai_type = "dataproc.googleapis.com/Cluster"

    def _get_request_args(self):
        return {
            'projectId': self._resource_data['project_id'],
            'region': self._resource_data['location'],
            'clusterName': self._resource_data['name']
        }

    def _update_request_args(self, body):
        return {
            'projectId': self._resource_data['project_id'],
            'region': self._resource_data['location'],
            'clusterName': self._resource_data['name']
        }


class GcpGkeCluster(GoogleAPIResource):

    service_name = "container"
    resource_path = "projects.locations.clusters"
    version = "v1"
    readiness_key = 'status'
    readiness_value = 'RUNNING'

    required_resource_data = ['name', 'location', 'project_id']

    cai_type = "container.googleapis.com/Cluster"

    def _get_request_args(self):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['name']
            )
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['name']
            ),
            'body': body
        }


class GcpGkeClusterNodepool(GoogleAPIResource):

    service_name = "container"
    resource_path = "projects.locations.clusters.nodePools"
    version = "v1"
    readiness_key = 'status'
    readiness_value = 'RUNNING'

    required_resource_data = ['name', 'cluster', 'location', 'project_id']

    cai_type = "container.googleapis.com/NodePool"  # beta

    def _get_request_args(self):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}/nodePools/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['cluster'],
                self._resource_data['name']
            )
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}/nodePools/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['cluster'],
                self._resource_data['name']
            ),
            'body': body
        }


class GcpPubsubSubscription(GoogleAPIResource):

    service_name = "pubsub"
    resource_path = "projects.subscriptions"
    version = "v1"
    update_method = "patch"

    required_resource_data = ['name', 'project_id']

    cai_type = "pubsub.googleapis.com/Subscription"

    def _get_request_args(self):
        return {
            'subscription': 'projects/{}/subscriptions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            )
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/subscriptions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            ),
            'body': {
                'subscription': body,
                'updateMask': 'labels,ack_deadline_seconds,push_config,message_retention_duration,retain_acked_messages,expiration_policy'
            }
        }


class GcpPubsubSubscriptionIam(GcpPubsubSubscription):

    resource_property = 'iam'
    parent_cls = GcpPubsubSubscription
    get_method = "getIamPolicy"
    update_method = "setIamPolicy"

    def _get_request_args(self):
        return {
            'resource': 'projects/{}/subscriptions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            )
        }

    def _update_request_args(self, body):
        return {
            'resource': 'projects/{}/subscriptions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
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

    required_resource_data = ['name', 'project_id']

    cai_type = "pubsub.googleapis.com/Topic"

    def _get_request_args(self):
        return {
            'topic': 'projects/{}/topics/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            )
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/topics/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            ),
            'body': {
                'topic': body,
                # the name field is immutable
                'updateMask': 'labels'
            }
        }


class GcpPubsubTopicIam(GcpPubsubTopic):

    resource_property = "iam"
    parent_cls = GcpPubsubTopic
    get_method = "getIamPolicy"
    update_method = "setIamPolicy"

    def _get_request_args(self):
        return {
            'resource': 'projects/{}/topics/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            )
        }

    def _update_request_args(self, body):
        return {
            'resource': 'projects/{}/topics/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            ),
            'body': {
                'policy': body
            }
        }


class GcpStorageBucket(GoogleAPIResource):

    service_name = "storage"
    resource_path = "buckets"
    version = "v1"

    required_resource_data = ['name']

    cai_type = "storage.googleapis.com/Bucket"

    def _get_request_args(self):
        return {
            'bucket': self._resource_data['name'],
        }

    def _update_request_args(self, body):
        return {
            'bucket': self._resource_data['name'],
            'body': body
        }


class GcpStorageBucketIamPolicy(GcpStorageBucket):

    resource_property = "iam"
    parent_cls = GcpStorageBucket
    get_method = "getIamPolicy"
    update_method = "setIamPolicy"


class GcpSqlInstance(GoogleAPIResource):

    service_name = "sqladmin"
    resource_path = "instances"
    version = "v1beta4"
    readiness_key = 'state'
    readiness_value = 'RUNNABLE'

    cai_type = "sqladmin.googleapis.com/Instance"

    def _get_request_args(self):
        return {
            'instance': self._resource_data['name'],
            'project': self._resource_data['project_id']
        }

    def _update_request_args(self, body):
        return {
            'instance': self._resource_data['name'],
            'project': self._resource_data['project_id'],
            'body': body
        }


class GcpProject(GoogleAPIResource):

    service_name = "cloudresourcemanager"
    resource_path = "projects"
    version = "v1"

    cai_type = "cloudresourcemanager.googleapis.com/Project"  # beta

    def _get_request_args(self):
        return {
            'projectId': self._resource_data['name']
        }

    def _update_request_args(self, body):
        return {
            'projectId': self._resource_data['name'],
            'body': body
        }


class GcpProjectIam(GcpProject):

    resource_property = "iam"
    parent_cls = GcpProject
    get_method = "getIamPolicy"
    update_method = "setIamPolicy"

    def _get_request_args(self):
        return {
            'resource': self._resource_data['name'],
            'body': {}
        }

    def _update_request_args(self, body):
        return {
            'resource': self._resource_data['name'],
            'body': {
                'policy': body,
                'updateMask': "bindings,etag,auditConfigs"
            }
        }


class GcpProjectService(GoogleAPIResource):

    service_name = "serviceusage"
    resource_path = "services"
    version = "v1"

    required_resource_data = ['name', 'project_id']

    cai_type = 'serviceusage.googleapis.com/Service'

    def _get_request_args(self):
        return {
            'name': 'projects/{}/services/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            )
        }

    def _update_request_args(self, body):
        raise NotImplementedError("Update request not available")
