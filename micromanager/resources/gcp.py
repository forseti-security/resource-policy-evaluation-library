from .base import Resource
from micromanager.exceptions import is_retryable_exception
import tenacity
from googleapiclienthelpers.discovery import build_subresource


class GoogleAPIResource(Resource):

    # Names of the get and update methods. Most are the same but override in
    # the Resource if necessary
    get_method = "get"
    update_method = "update"

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

        self.resource_data = resource_data

    @staticmethod
    def factory(resource_data, **kargs):
        resource_type_map = {
            'storage.buckets': GcpStorageBucket,
            'bigquery.datasets': GcpBigqueryDataset,
            'sqladmin.instances': GcpSqlInstance
        }

        resource_type = resource_data.get('resource_type')
        if not resource_type:
            assert 0, 'Unrecognized resource'

        if resource_type not in resource_type_map:
            assert 0, 'Unrecognized resource'

        cls = resource_type_map.get(resource_type)
        return cls(resource_data, **kargs)

    def type(self):
        return ".".join(["gcp", self.service_name, self.resource_path])

    def get(self):
        method = getattr(self.service, self.get_method)
        return method(**self._get_request_args()).execute()

    @tenacity.retry(
        retry=tenacity.retry_if_exception(is_retryable_exception),
        wait=tenacity.wait_random_exponential(multiplier=1, max=10),
        stop=tenacity.stop_after_attempt(10)
    )
    def update(self, body):
        print('trying')
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


class GcpStorageBucket(GoogleAPIResource):

    service_name = "storage"
    resource_path = "buckets"
    version = "v1"

    def _get_request_args(self):
        return {
            'bucket': self.resource_data['resource_name']
        }

    def _update_request_args(self, body):
        return {
            'bucket': self.resource_data['resource_name'],
            'body': body
        }


class GcpSqlInstance(GoogleAPIResource):

    service_name = "sqladmin"
    resource_path = "instances"
    version = "v1beta4"

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
