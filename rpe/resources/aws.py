import boto3
from .base import Resource

class AwsResource(Resource):

    @staticmethod
    def factory(resource_data, **kargs):
        resource_type_map = {
            'ec2.instance': AwsEc2Instance,
        }

        resource_type = resource_data.get('resource_type')
        if not resource_type:
            assert 0, 'Unrecognized resource'

        if resource_type not in resource_type_map:
            assert 0, 'Unrecognized resource'

        cls = resource_type_map.get(resource_type)
        return cls(resource_data, **kargs)

    def __init__(self, resource_data):
        self.resource_data = resource_data
        self.client = boto3.client(self.service_name)

    def get(self):
        method = getattr(self.client, self.get_method)
        resp = method(**self._get_request_args())
        return resp

    def remediate(self):
        pass

    def type(self):
        return "aws.{}".format(self._type)

class AwsEc2Instance(AwsResource):

    service_name = 'ec2'
    _type = 'ec2.instance'
    resource_path="instances"
    get_method = 'describe_instances'

    def _get_request_args(self):
        return {
            'InstanceIds': [
                self.resource_data.get('resource_name'),
            ]
        }
