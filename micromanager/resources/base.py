from abc import ABC, abstractmethod


class Resource(ABC):

    @staticmethod
    def factory(platform, resource_data, **kargs):
        """ Return a resource from the appropriate platform """
        from .gcp import GoogleAPIResource

        resource_platform_map = {
            'gcp': GoogleAPIResource
        }

        try:
            resource = resource_platform_map[platform].factory(
                resource_data,
                **kargs
            )
        except KeyError:
            raise AttributeError('Unrecognized platform')

        return resource

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def type(self):
        pass
