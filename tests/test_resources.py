# Copyright 2019 The resource-policy-evaluation-library Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytest

from rpe.resources import Resource
from rpe.resources.gcp import GcpBigqueryDataset
from rpe.resources.gcp import GcpComputeInstance
from rpe.resources.gcp import GcpSqlInstance
from rpe.resources.gcp import GcpStorageBucket
from rpe.resources.gcp import GcpStorageBucketIamPolicy

test_project = "my_project"
test_resource_name = "my_resource"

test_cases = [
    (
        {
            'resource_type': 'bigquery.datasets',
            'resource_name': test_resource_name,
            'project_id': test_project
        },
        GcpBigqueryDataset,
        'gcp.bigquery.datasets',
        '//bigquery.googleapis.com/projects/my_project/datasets/my_resource'
    ),
    (
        {
            'resource_type': 'compute.instances',
            'resource_name': test_resource_name,
            'resource_location': 'us-central1-a',
            'project_id': test_project
        },
        GcpComputeInstance,
        'gcp.compute.instances',
        '//compute.googleapis.com/projects/my_project/zones/us-central1-a/instances/my_resource'
    ),
    (
        {
            'resource_type': 'sqladmin.instances',
            'resource_name': test_resource_name,
            'project_id': test_project
        },
        GcpSqlInstance,
        'gcp.sqladmin.instances',
        '//sql.googleapis.com/projects/my_project/instances/my_resource'
    ),
    (
        {
            'resource_type': 'storage.buckets',
            'resource_name': test_resource_name,
            'project_id': test_project
        },
        GcpStorageBucket,
        'gcp.storage.buckets',
        '//storage.googleapis.com/buckets/my_resource'
    ),
    (
        {
            'resource_type': 'storage.buckets.iam',
            'resource_name': test_resource_name,
            'project_id': test_project
        },
        GcpStorageBucketIamPolicy,
        'gcp.storage.buckets.iam',
        '//storage.googleapis.com/buckets/my_resource'
    )
]


@pytest.mark.parametrize(
    "input,cls,rtype",
    [(c[0], c[1], c[2]) for c in test_cases],
    ids=[c[1].__name__ for c in test_cases])
def test_gcp_resource_factory(input, cls, rtype):
    r = Resource.factory("gcp", input)
    assert r.__class__ == cls
    assert r.type() == rtype


def test_gcp_resource_factory_invalid():
    with pytest.raises(AssertionError):
        Resource.factory('gcp', {})

@pytest.mark.parametrize(
    "input,frn",
    [(c[0], c[3]) for c in test_cases],
    ids=[c[1].__name__ for c in test_cases])
def test_gcp_full_resource_name(input, frn):
    r = Resource.factory("gcp", input)
    assert r.full_resource_name() == frn
