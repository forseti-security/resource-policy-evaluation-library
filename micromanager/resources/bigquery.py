from .base import GoogleAPIResourceBase


class BQDataset(GoogleAPIResourceBase):

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
