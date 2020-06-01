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

    # Names of the get method of the root resource
    get_method = "get"
    required_resource_data = ['name']

    # Other properties of a resource we might need to perform evaluations, such as iam policy
    resource_components = {}

    # If a resource is not in a ready state, we can't update it. If we retrieve
    # it, and the state changes, updates will be rejected because the ETAG will
    # have changed. If a resource defines readiness criteria, the get() call
    # will wait until the resource is in a ready state to return
    #
    # Key/Value to check to see if a resource is ready
    readiness_key = None
    readiness_value = None
    readiness_terminal_values = []

    def __init__(self, client_kwargs={}, **resource_data):

        # Set some defaults
        self._service = None

        # Load and validate additional resource data
        self._resource_data = resource_data
        self._validate_resource_data()

        # Store the client kwargs to pass to any new clients
        self._client_kwargs = client_kwargs

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

    @staticmethod
    def _extract_cai_name_data(name):
        ''' Attempt to get identifiable information out of a Cloud Asset Inventory-formatted resource_name '''

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

    @classmethod
    def subclass_by_type(cls, resource_type):
        mapper = {
            res_cls.resource_type: res_cls

            for res_cls in cls.__subclasses__()
        }

        try:
            return mapper[resource_type]
        except KeyError:
            raise ResourceException('Unrecognized resource type: {}'.format(resource_type))

    @classmethod
    def from_resource_data(cls, *, resource_type, client_kwargs={}, **resource_data):
        res_cls = cls.subclass_by_type(resource_type)
        return res_cls(client_kwargs=client_kwargs, **resource_data)

    @staticmethod
    def from_cai_data(resource_name, resource_type, project_id=None, client_kwargs={}):
        ''' Attempt to return the appropriate resource using Cloud Asset Inventory-formatted resource info '''

        res_cls = GoogleAPIResource.subclass_by_type(resource_type)

        resource_data = GoogleAPIResource._extract_cai_name_data(resource_name)

        # if the project_id was passed, and its wasnt found in the resource name, add it
        if project_id and 'project_id' not in resource_data:
            resource_data['project_id'] = project_id

        return res_cls(
            client_kwargs=client_kwargs,
            **resource_data
        )

    def to_dict(self):
        details = self._resource_data.copy()
        details.update({
            'resource_type': self.resource_type,
        })

        try:
            details['full_resource_name'] = self.full_resource_name()
        except Exception:
            details['full_resource_name'] = None

        return details

    def type(self):
        return self.resource_type

    # Google's documentation describes what it calls a 'full resource name' for
    # resources. None of the API's seem to implement it (except Cloud Asset
    # Inventory). This attempts to generate it from the discovery-based api
    # client's generated http request url.
    #
    # If we inject it into the resource, we can use it in policy evaluation to
    # simplify the structure of our policies
    def full_resource_name(self):

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

    def _get_component(self, component):
        method_name = self.resource_components[component]

        # Many components take the same request signature, but allow for custom request
        # args if needed. Fall back to default args if the expected function doesn't exist
        if hasattr(self, f'_get_{component}_request_args'):
            req_arg_method = getattr(self, f'_get_{component}_request_args')
        else:
            req_arg_method = getattr(self, '_get_request_args')
        
        method = getattr(self.service, method_name)
        
        component_metadata = method(**req_arg_method()).execute()
        return component_metadata
        

    def get(self):
        method = getattr(self.service, self.get_method)

        # If the resource has readiness criteria, wait for it
        if self.readiness_key and self.readiness_value:
            waiter = Waiter(method, **self._get_request_args())
            asset = waiter.wait(
                self.readiness_key,
                self.readiness_value,
                terminal_values=self.readiness_terminal_values,
                interval=10,
                retries=90
            )
        else:
            asset = method(**self._get_request_args()).execute()

        resp = {
            'type': self.type(),
            'name': self.full_resource_name(),
        }

        resp['resource'] = asset

        for c in self.resource_components:
            resp[c] = self._get_component(c)

        return resp

    # Determine what remediation steps to take, allow for future remediation specifications
    def remediate(self, remediation):
        # Check for an update spec version, default to version 1
        remediation_spec = remediation.get('_remediation_spec', "")

        if remediation_spec in ['v2beta1', 'v2']:
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


class GcpAppEngineInstance(GoogleAPIResource):

    service_name = "appengine"
    resource_path = "apps.services.versions.instances"
    version = "v1"
    readiness_key = 'vmStatus'
    readiness_value = 'RUNNING'

    resource_type = 'appengine.googleapis.com/Instance'  # this is made-up based on existing appengine types

    required_resource_data = ['name', 'app', 'service', 'version']

    def _get_request_args(self):
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

    resource_type = "bigquery.googleapis.com/Dataset"

    def _get_request_args(self):
        return {
            'datasetId': self._resource_data['name'],
            'projectId': self._resource_data['project_id']
        }


class GcpBigtableInstance(GoogleAPIResource):

    service_name = "bigtableadmin"
    resource_path = "projects.instances"
    version = "v2"
    readiness_key = 'state'
    readiness_value = 'READY'

    resource_components = {
        'iam': 'getIamPolicy',
    }

    required_resource_data = ['name', 'project_id']

    resource_type = "bigtableadmin.googleapis.com/Instance"

    def _get_request_args(self):
        return {
            'name': 'projects/{}/instances/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            ),
        }


class GcpCloudFunction(GoogleAPIResource):

    service_name = "cloudfunctions"
    resource_path = "projects.locations.functions"
    version = "v1"

    resource_components = {
        'iam': 'getIamPolicy',
    }

    required_resource_data = ['name', 'location', 'project_id']

    resource_type = "cloudfunctions.googleapis.com/CloudFunction"  # unreleased

    def _get_request_args(self):
        return {
            'name': 'projects/{}/locations/{}/functions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['name']
            ),
        }

    # The top-level dict key is different
    def _get_iam_request_args(self):
        return {
            'resource': 'projects/{}/locations/{}/functions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['name']
            ),
        }


class GcpComputeInstance(GoogleAPIResource):

    service_name = "compute"
    resource_path = "instances"
    version = "v1"

    required_resource_data = ['name', 'location', 'project_id']

    resource_type = "compute.googleapis.com/Instance"

    def _get_request_args(self):
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

    resource_type = "compute.googleapis.com/Disk"

    def _get_request_args(self):
        return {
            'project': self._resource_data['project_id'],
            'zone': self._resource_data['location'],
            'disk': self._resource_data['name']
        }


class GcpComputeSubnetwork(GoogleAPIResource):

    service_name = "compute"
    resource_path = "subnetworks"
    version = "v1"

    required_resource_data = ['name', 'location', 'project_id']

    resource_type = "compute.googleapis.com/Subnetwork"

    def _get_request_args(self):
        return {
            'project': self._resource_data['project_id'],
            'region': self._resource_data['location'],
            'subnetwork': self._resource_data['name']
        }


class GcpComputeFirewall(GoogleAPIResource):

    service_name = "compute"
    resource_path = "firewalls"
    version = "v1"

    required_resource_data = ['name', 'project_id']

    resource_type = "compute.googleapis.com/Firewall"

    def _get_request_args(self):
        return {
            'firewall': self._resource_data['name'],
            'project': self._resource_data['project_id']
        }



class GcpDataprocCluster(GoogleAPIResource):
    service_name = "dataproc"
    resource_path = "projects.regions.clusters"
    version = "v1beta2"

    required_resource_data = ['name', 'location', 'project_id']

    resource_type = "dataproc.googleapis.com/Cluster"

    def _get_request_args(self):
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
    readiness_terminal_values = ['ERROR', 'DEGRADED', 'STOPPING', 'STATUS_UNSPECIFIED']

    required_resource_data = ['name', 'location', 'project_id']

    resource_type = "container.googleapis.com/Cluster"

    def _get_request_args(self):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['name']
            )
        }



class GcpGkeClusterNodepool(GoogleAPIResource):

    service_name = "container"
    resource_path = "projects.locations.clusters.nodePools"
    version = "v1"
    readiness_key = 'status'
    readiness_value = 'RUNNING'

    required_resource_data = ['name', 'cluster', 'location', 'project_id']

    resource_type = "container.googleapis.com/NodePool"  # beta

    def _get_request_args(self):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}/nodePools/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['cluster'],
                self._resource_data['name']
            )
        }



class GcpPubsubSubscription(GoogleAPIResource):

    service_name = "pubsub"
    resource_path = "projects.subscriptions"
    version = "v1"

    required_resource_data = ['name', 'project_id']

    resource_components = {
        'iam': 'getIamPolicy',
    }

    resource_type = "pubsub.googleapis.com/Subscription"

    def _get_request_args(self):
        return {
            'subscription': 'projects/{}/subscriptions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            )
        }

    def _get_iam_request_args(self):
        return {
            'resource': 'projects/{}/subscriptions/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            )
        }



class GcpPubsubTopic(GoogleAPIResource):

    service_name = "pubsub"
    resource_path = "projects.topics"
    version = "v1"

    required_resource_data = ['name', 'project_id']

    resource_components = {
        'iam': 'getIamPolicy',
    }

    resource_type = "pubsub.googleapis.com/Topic"

    def _get_request_args(self):
        return {
            'topic': 'projects/{}/topics/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            )
        }

    def _get_iam_request_args(self):
        return {
            'resource': 'projects/{}/topics/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            )
        }



class GcpStorageBucket(GoogleAPIResource):

    service_name = "storage"
    resource_path = "buckets"
    version = "v1"

    resource_components = {
        'iam': 'getIamPolicy',
    }

    required_resource_data = ['name']

    resource_type = "storage.googleapis.com/Bucket"

    def _get_request_args(self):
        return {
            'bucket': self._resource_data['name'],
        }


class GcpSqlInstance(GoogleAPIResource):

    service_name = "sqladmin"
    resource_path = "instances"
    version = "v1beta4"
    readiness_key = 'state'
    readiness_value = 'RUNNABLE'
    readiness_terminal_values = ['FAILED', 'MAINTENANCE', 'SUSPENDED', 'UNKNOWN_STATE']

    resource_type = "sqladmin.googleapis.com/Instance"

    def _get_request_args(self):
        return {
            'instance': self._resource_data['name'],
            'project': self._resource_data['project_id']
        }


class GcpProject(GoogleAPIResource):

    service_name = "cloudresourcemanager"
    resource_path = "projects"
    version = "v1"

    resource_components = {
        'iam': 'getIamPolicy',
    }

    resource_type = "cloudresourcemanager.googleapis.com/Project"  # beta

    def _get_request_args(self):
        return {
            'projectId': self._resource_data['name']
        }

    def _get_iam_request_args(self):
        return {
            'resource': self._resource_data['name'],
            'body': {}
        }


class GcpProjectService(GoogleAPIResource):

    service_name = "serviceusage"
    resource_path = "services"
    version = "v1"

    required_resource_data = ['name', 'project_id']

    resource_type = 'serviceusage.googleapis.com/Service'

    def _get_request_args(self):
        return {
            'name': 'projects/{}/services/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['name']
            )
        }
