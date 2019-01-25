from .base import GoogleAPIResourceBase


class Bucket(GoogleAPIResourceBase):

    get_method = "get"
    service_name = "storage"
    resource_path = "buckets"
    version = "v1"

    def _get_request_args(self):
        return {
            'bucket': self.resource_data['resource_name']
        }
