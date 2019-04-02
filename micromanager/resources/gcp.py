# Copyright 2019 The micromanager Authors. All rights reserved.
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


from .base import Resource
from micromanager.exceptions import is_retryable_exception
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
            'bigquery.datasets': GcpBigqueryDataset,
            'compute.instances': GcpComputeInstance,
            'cloudresourcemanager.projects': GcpProject,
            'cloudresourcemanager.projects.iam': GcpProjectIam,
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

    def get(self):
        method = getattr(self.service, self.get_method)

        # If the resource has readiness criteria, wait for it
        if self.readiness_key and self.readiness_value:
            waiter = Waiter(method, **self._get_request_args())
            asset = waiter.wait(
                self.readiness_key,
                self.readiness_value,
                interval=7,
                retries=60
            )
        else:
            asset = method(**self._get_request_args()).execute()

        # if this asset is a property, inject its parent
        if self.is_property():
            parent = self.parent_resource.get()
            asset['_resource'] = parent
        return asset

    @tenacity.retry(
        retry=tenacity.retry_if_exception(is_retryable_exception),
        wait=tenacity.wait_random_exponential(multiplier=1, max=10),
        stop=tenacity.stop_after_attempt(10)
    )
    def update(self, body):

        # remove injected data before attempting update
        if self.is_property() and '_resource' in body:
            del body['_resource']

        method = getattr(self.service, self.update_method)
        return method(**self._update_request_args(body)).execute()


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
            'resource': self.resource_data['resource_name']
        }

    def _update_request_args(self, body):
        return {
            'resource': self.resource_data['resource_name'],
            'body': body
        }
