from .base import ResourceBase   # noqa F401
from .bucket import Bucket       # noqa F401
from .sql import SQLInstance     # noqa F401
from .bigquery import BQDataset  # noqa F401


class Resource():

    @staticmethod
    def factory(resource_data, **kargs):
        resource_kind_map = {
            'storage#bucket': Bucket,
            'bigquery#dataset': BQDataset,
            'sql#instance': SQLInstance
        }

        kind = resource_data.get('resource_kind')
        if not kind:
            assert 0, 'Unrecognized resource'

        if kind not in resource_kind_map:
            assert 0, 'Unrecognized resource'

        cls = resource_kind_map.get(kind)
        return cls(resource_data, **kargs)
