from abc import ABCMeta, abstractmethod
from googleapiclienthelpers.discovery import build_subresource


class ResourceBase(metaclass=ABCMeta):

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def update(self):
        pass


class GoogleAPIResourceBase(ResourceBase, metaclass=ABCMeta):

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

    def type(self):
        return ".".join(["gcp", self.service_name, self.resource_path])

    def get(self):
        method = getattr(self.service, self.get_method)
        return method(**self._get_request_args()).execute()

    def update(self, body):
        method = getattr(self.service, self.update_method)
        return method(**self._update_request_args(body)).execute()
