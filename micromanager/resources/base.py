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

    def get(self):
        method = getattr(self.service, self.get_method)

        return method(**self._get_request_args()).execute()

    def update(self):
        pass
