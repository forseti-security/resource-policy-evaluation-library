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


import collections
import pytest

from google.oauth2.credentials import Credentials

from rpe.exceptions import ResourceException
from rpe.resources.gcp import GoogleAPIResource
from rpe.resources.gcp import GcpAppEngineInstance
from rpe.resources.gcp import GcpBigqueryDataset
from rpe.resources.gcp import GcpBigtableInstance
from rpe.resources.gcp import GcpCloudFunction
from rpe.resources.gcp import GcpComputeInstance
from rpe.resources.gcp import GcpComputeDisks
from rpe.resources.gcp import GcpDataprocCluster
from rpe.resources.gcp import GcpGkeCluster
from rpe.resources.gcp import GcpGkeClusterNodepool
from rpe.resources.gcp import GcpProject
from rpe.resources.gcp import GcpProjectService
from rpe.resources.gcp import GcpPubsubSubscription
from rpe.resources.gcp import GcpPubsubTopic
from rpe.resources.gcp import GcpSqlInstance
from rpe.resources.gcp import GcpStorageBucket
from rpe.resources.gcp import GcpComputeFirewall
from rpe.resources.gcp import GcpComputeSubnetwork

test_project = "my_project"
test_resource_name = "my_resource"
client_kwargs = {
    'credentials': Credentials(token='')
}

ResourceTestCase = collections.namedtuple('ResourceTestCase', 'resource_data cls resource_type name')

test_cases = [
    ResourceTestCase(
        resource_data={
            'name': 'my_resource',
            'app': 'my_project',
            'service': 'default',
            'version': '0123456789',
            'project_id': test_project,
        },
        cls=GcpAppEngineInstance,
        resource_type='appengine.googleapis.com/Instance',
        name='//appengine.googleapis.com/apps/my_project/services/default/versions/0123456789/instances/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpBigqueryDataset,
        resource_type='bigquery.googleapis.com/Dataset',
        name='//bigquery.googleapis.com/projects/my_project/datasets/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpBigtableInstance,
        resource_type='bigtableadmin.googleapis.com/Instance',
        name='//bigtable.googleapis.com/projects/my_project/instances/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'location': 'us-central1-a',
            'project_id': test_project
        },
        cls=GcpCloudFunction,
        resource_type='cloudfunctions.googleapis.com/CloudFunction',
        name='//cloudfunctions.googleapis.com/projects/my_project/locations/us-central1-a/functions/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'location': 'us-central1-a',
            'project_id': test_project
        },
        cls=GcpComputeDisks,
        resource_type='compute.googleapis.com/Disk',
        name='//compute.googleapis.com/projects/my_project/zones/us-central1-a/disks/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'location': 'us-central1-a',
            'project_id': test_project
        },
        cls=GcpComputeInstance,
        resource_type='compute.googleapis.com/Instance',
        name='//compute.googleapis.com/projects/my_project/zones/us-central1-a/instances/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'location': 'us-central1-a',
            'project_id': test_project
        },
        cls=GcpGkeCluster,
        resource_type='container.googleapis.com/Cluster',
        name='//container.googleapis.com/projects/my_project/locations/us-central1-a/clusters/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'location': 'us-central1-a',
            'cluster': 'parent_resource',
            'project_id': test_project
        },
        cls=GcpGkeClusterNodepool,
        resource_type='container.googleapis.com/NodePool',
        name='//container.googleapis.com/projects/my_project/locations/us-central1-a/clusters/parent_resource/nodePools/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_project,
            'project_id': test_project
        },
        cls=GcpProject,
        resource_type='cloudresourcemanager.googleapis.com/Project',
        name='//cloudresourcemanager.googleapis.com/projects/my_project'
    ),
    ResourceTestCase(
        resource_data={
            'name': 'compute.googleapis.com',
            'project_id': test_project
        },
        cls=GcpProjectService,
        resource_type='serviceusage.googleapis.com/Service',
        name='//serviceusage.googleapis.com/projects/my_project/services/compute.googleapis.com'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'location': 'global',
            'project_id': test_project
        },
        cls=GcpDataprocCluster,
        resource_type='dataproc.googleapis.com/Cluster',
        name='//dataproc.googleapis.com/projects/my_project/regions/global/clusters/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpPubsubSubscription,
        resource_type='pubsub.googleapis.com/Subscription',
        name='//pubsub.googleapis.com/projects/my_project/subscriptions/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpPubsubTopic,
        resource_type='pubsub.googleapis.com/Topic',
        name='//pubsub.googleapis.com/projects/my_project/topics/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpSqlInstance,
        resource_type='sqladmin.googleapis.com/Instance',
        name='//cloudsql.googleapis.com/projects/my_project/instances/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpStorageBucket,
        resource_type='storage.googleapis.com/Bucket',
        # This should include the collection name `/buckets/`, but CAI doesn't do that
        # See: https://issuetracker.google.com/issues/131586763
        name='//storage.googleapis.com/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'location': 'us-central1',
            'project_id': test_project
        },
        cls=GcpComputeSubnetwork,
        resource_type='compute.googleapis.com/Subnetwork',
        name='//compute.googleapis.com/projects/my_project/regions/us-central1/subnetworks/my_resource'
    ),
    ResourceTestCase(
        resource_data={
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpComputeFirewall,
        resource_type='compute.googleapis.com/Firewall',
        name='//compute.googleapis.com/projects/my_project/global/firewalls/my_resource'
    )
]


@pytest.mark.parametrize(
    "case",
    test_cases,
    ids=[case.cls.__name__ for case in test_cases])
def test_gcp_from_resource(case):
    r = GoogleAPIResource.from_resource_data(resource_type=case.resource_type, client_kwargs=client_kwargs, **case.resource_data)
    assert r.__class__ == case.cls
    assert isinstance(r._get_request_args(), dict)


def test_gcp_from_resource_no_type():
    with pytest.raises(TypeError) as excinfo:
        GoogleAPIResource.from_resource_data(project_id=test_project)

    assert 'required keyword-only argument' in str(excinfo.value)
    assert 'resource_type' in str(excinfo.value)


def test_gcp_resource_bad_type():
    with pytest.raises(ResourceException) as excinfo:
        GoogleAPIResource.from_resource_data(resource_type='fake.type')

    assert 'Unrecognized resource type' in str(excinfo.value)


@pytest.mark.parametrize(
    "case",
    test_cases,
    ids=[case.cls.__name__ for case in test_cases])
def test_gcp_full_resource_name(case):
    r = GoogleAPIResource.from_resource_data(resource_type=case.resource_type, client_kwargs=client_kwargs, **case.resource_data)
    assert r.full_resource_name() == case.name


def test_missing_resource_data():
    with pytest.raises(ResourceException) as excinfo:

        GcpAppEngineInstance(name=test_resource_name)

    assert "Missing data required for resource creation" in str(excinfo.value)


def test_gcp_to_dict():
    r = GoogleAPIResource.from_resource_data(
        resource_type='storage.googleapis.com/Bucket',
        client_kwargs=client_kwargs,
        name=test_resource_name,
        project_id=test_project,
    )

    data = r.to_dict()
    # with no creds, we should still get this key but it should be none
    assert data['project_id'] == test_project
