from .base import GoogleAPIResourceBase


class SQLInstance(GoogleAPIResourceBase):

    get_method = "get"
    service_name = "sqladmin"
    resource_path = "instances"
    version = "v1beta4"

    def _get_request_args(self):
        return {
            'instance': self.resource_data['resource_name'],
            'project': self.resource_data['project_id']
        }
