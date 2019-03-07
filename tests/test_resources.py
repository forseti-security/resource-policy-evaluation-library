import pytest

from micromanager.resources import Resource
from micromanager.resources.gcp import GcpBigqueryDataset
from micromanager.resources.gcp import GcpComputeInstance
from micromanager.resources.gcp import GcpSqlInstance
from micromanager.resources.gcp import GcpStorageBucket
from micromanager.resources.gcp import GcpStorageBucketIamPolicy

test_cases = [
    (
        {
            'resource_type': 'bigquery.datasets',
            'resource_name': '',
            'project_id': ''
        },
        GcpBigqueryDataset,
        'gcp.bigquery.datasets'
    ),
    (
        {
            'resource_type': 'compute.instances',
            'resource_name': '',
            'project_id': ''
        },
        GcpComputeInstance,
        'gcp.compute.instances'
    ),
    (
        {
            'resource_type': 'sqladmin.instances',
            'resource_name': '',
            'project_id': ''
        },
        GcpSqlInstance,
        'gcp.sqladmin.instances'
    ),
    (
        {
            'resource_type': 'storage.buckets',
            'resource_name': '',
            'project_id': ''
        },
        GcpStorageBucket,
        'gcp.storage.buckets'
    ),
    (
        {
            'resource_type': 'storage.buckets.iam',
            'resource_name': '',
            'project_id': ''
        },
        GcpStorageBucketIamPolicy,
        'gcp.storage.buckets.iam'
    )
]


@pytest.mark.parametrize(
    "input,cls,rtype",
    test_cases,
    ids=[cls.__name__ for (_, cls, _) in test_cases])
def test_gcp_resource_factory(input, cls, rtype):
    r = Resource.factory("gcp", input)
    assert r.__class__ == cls
    assert r.type() == rtype


def test_gcp_resource_factory_invalid():
    with pytest.raises(AssertionError):
        Resource.factory('gcp', {})
