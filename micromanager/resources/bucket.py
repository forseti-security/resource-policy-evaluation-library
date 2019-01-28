from .base import GoogleAPIResourceBase


class Bucket(GoogleAPIResourceBase):

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
