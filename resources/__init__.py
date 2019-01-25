from .base import ResourceBase   # noqa F401
from .bucket import Bucket       # noqa F401
from .sql import SQLInstance     # noqa F401
from .bigquery import BQDataset  # noqa F401


def resource_lookup(context):

    resource_kind_map = {
        'storage#bucket': Bucket,
        'bigquery#dataset': BQDataset,
        'sql#instance': SQLInstance
    }

    kind = context.get('resource_kind')
    if not kind:
        return None

    if kind not in resource_kind_map:
        return None

    return resource_kind_map.get(kind)
