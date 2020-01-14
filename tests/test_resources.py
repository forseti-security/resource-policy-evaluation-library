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
from rpe.resources import Resource
from rpe.resources.gcp import GcpAppEngineInstance
from rpe.resources.gcp import GcpBigqueryDataset
from rpe.resources.gcp import GcpBigtableInstance
from rpe.resources.gcp import GcpBigtableInstanceIam
from rpe.resources.gcp import GcpCloudFunction
from rpe.resources.gcp import GcpCloudFunctionIam
from rpe.resources.gcp import GcpComputeInstance
from rpe.resources.gcp import GcpComputeDisks
from rpe.resources.gcp import GcpDataprocCluster
from rpe.resources.gcp import GcpGkeCluster
from rpe.resources.gcp import GcpGkeClusterNodepool
from rpe.resources.gcp import GcpProject
from rpe.resources.gcp import GcpProjectIam
from rpe.resources.gcp import GcpProjectService
from rpe.resources.gcp import GcpPubsubSubscription
from rpe.resources.gcp import GcpPubsubSubscriptionIam
from rpe.resources.gcp import GcpPubsubTopic
from rpe.resources.gcp import GcpPubsubTopicIam
from rpe.resources.gcp import GcpSqlInstance
from rpe.resources.gcp import GcpStorageBucket
from rpe.resources.gcp import GcpStorageBucketIamPolicy
from rpe.resources.gcp import GcpComputeFirewall
from rpe.resources.gcp import GcpComputeSubnetwork

test_project = "my_project"
test_resource_name = "my_resource"
client_kwargs = {
    'credentials': Credentials(token='')
}

ResourceTestCase = collections.namedtuple('ResourceTestCase', 'input cls type name')

test_cases = [
    ResourceTestCase(
        input={
            'resource_type': 'apps.services.versions.instances',
            'name': 'my_resource',
            'app': 'my_project',
            'service': 'default',
            'version': '0123456789',
            'project_id': test_project,
        },
        cls=GcpAppEngineInstance,
        type='gcp.appengine.apps.services.versions.instances',
        name='//appengine.googleapis.com/apps/my_project/services/default/versions/0123456789/instances/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'bigquery.datasets',
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpBigqueryDataset,
        type='gcp.bigquery.datasets',
        name='//bigquery.googleapis.com/projects/my_project/datasets/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'bigtableadmin.projects.instances',
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpBigtableInstance,
        type='gcp.bigtableadmin.projects.instances',
        name='//bigtableadmin.googleapis.com/projects/my_project/instances/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'bigtableadmin.projects.instances.iam',
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpBigtableInstanceIam,
        type='gcp.bigtableadmin.projects.instances.iam',
        name='//bigtableadmin.googleapis.com/projects/my_project/instances/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'cloudfunctions.projects.locations.functions',
            'name': test_resource_name,
            'location': 'us-central1-a',
            'project_id': test_project
        },
        cls=GcpCloudFunction,
        type='gcp.cloudfunctions.projects.locations.functions',
        name='//cloudfunctions.googleapis.com/projects/my_project/locations/us-central1-a/functions/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'cloudfunctions.projects.locations.functions.iam',
            'name': test_resource_name,
            'location': 'us-central1-a',
            'project_id': test_project
        },
        cls=GcpCloudFunctionIam,
        type='gcp.cloudfunctions.projects.locations.functions.iam',
        name='//cloudfunctions.googleapis.com/projects/my_project/locations/us-central1-a/functions/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'compute.disks',
            'name': test_resource_name,
            'location': 'us-central1-a',
            'project_id': test_project
        },
        cls=GcpComputeDisks,
        type='gcp.compute.disks',
        name='//compute.googleapis.com/projects/my_project/zones/us-central1-a/disks/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'compute.instances',
            'name': test_resource_name,
            'location': 'us-central1-a',
            'project_id': test_project
        },
        cls=GcpComputeInstance,
        type='gcp.compute.instances',
        name='//compute.googleapis.com/projects/my_project/zones/us-central1-a/instances/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'container.projects.locations.clusters',
            'name': test_resource_name,
            'location': 'us-central1-a',
            'project_id': test_project
        },
        cls=GcpGkeCluster,
        type='gcp.container.projects.locations.clusters',
        name='//container.googleapis.com/projects/my_project/locations/us-central1-a/clusters/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'container.projects.locations.clusters.nodePools',
            'name': test_resource_name,
            'location': 'us-central1-a',
            'cluster': 'parent_resource',
            'project_id': test_project
        },
        cls=GcpGkeClusterNodepool,
        type='gcp.container.projects.locations.clusters.nodePools',
        name='//container.googleapis.com/projects/my_project/locations/us-central1-a/clusters/parent_resource/nodePools/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'cloudresourcemanager.projects',
            'name': test_project,
            'project_id': test_project
        },
        cls=GcpProject,
        type='gcp.cloudresourcemanager.projects',
        name='//cloudresourcemanager.googleapis.com/projects/my_project'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'cloudresourcemanager.projects.iam',
            'name': test_project,
            'project_id': test_project
        },
        cls=GcpProjectIam,
        type='gcp.cloudresourcemanager.projects.iam',
        name='//cloudresourcemanager.googleapis.com/projects/my_project'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'serviceusage.services',
            'name': 'compute.googleapis.com',
            'project_id': test_project
        },
        cls=GcpProjectService,
        type='gcp.serviceusage.services',
        name='//serviceusage.googleapis.com/projects/my_project/services/compute.googleapis.com'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'dataproc.clusters',
            'name': test_resource_name,
            'location': 'global',
            'project_id': test_project
        },
        cls=GcpDataprocCluster,
        type='gcp.dataproc.projects.regions.clusters',
        name='//dataproc.googleapis.com/projects/my_project/regions/global/clusters/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'pubsub.projects.subscriptions',
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpPubsubSubscription,
        type='gcp.pubsub.projects.subscriptions',
        name='//pubsub.googleapis.com/projects/my_project/subscriptions/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'pubsub.projects.subscriptions.iam',
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpPubsubSubscriptionIam,
        type='gcp.pubsub.projects.subscriptions.iam',
        name='//pubsub.googleapis.com/projects/my_project/subscriptions/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'pubsub.projects.topics',
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpPubsubTopic,
        type='gcp.pubsub.projects.topics',
        name='//pubsub.googleapis.com/projects/my_project/topics/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'pubsub.projects.topics.iam',
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpPubsubTopicIam,
        type='gcp.pubsub.projects.topics.iam',
        name='//pubsub.googleapis.com/projects/my_project/topics/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'sqladmin.instances',
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpSqlInstance,
        type='gcp.sqladmin.instances',
        name='//cloudsql.googleapis.com/projects/my_project/instances/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'storage.buckets',
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpStorageBucket,
        type='gcp.storage.buckets',
        name='//storage.googleapis.com/buckets/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'storage.buckets.iam',
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpStorageBucketIamPolicy,
        type='gcp.storage.buckets.iam',
        name='//storage.googleapis.com/buckets/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'compute.subnetworks',
            'name': test_resource_name,
            'location': 'us-central1',
            'project_id': test_project
        },
        cls=GcpComputeSubnetwork,
        type='gcp.compute.subnetworks',
        name='//compute.googleapis.com/projects/my_project/regions/us-central1/subnetworks/my_resource'
    ),
    ResourceTestCase(
        input={
            'resource_type': 'compute.firewalls',
            'name': test_resource_name,
            'project_id': test_project
        },
        cls=GcpComputeFirewall,
        type='gcp.compute.firewalls',
        name='//compute.googleapis.com/projects/my_project/global/firewalls/my_resource'
    )
]


@pytest.mark.parametrize(
    "case",
    test_cases,
    ids=[case.cls.__name__ for case in test_cases])
def test_gcp_resource_factory(case):
    r = Resource.factory("gcp", **case.input, client_kwargs=client_kwargs)
    assert r.__class__ == case.cls
    assert r.type() == case.type


def test_gcp_resource_factory_invalid():
    with pytest.raises(ResourceException):
        Resource.factory('gcp')


@pytest.mark.parametrize(
    "case",
    test_cases,
    ids=[case.cls.__name__ for case in test_cases])
def test_gcp_full_resource_name(case):
    r = Resource.factory("gcp", **case.input, client_kwargs=client_kwargs)
    assert r.full_resource_name() == case.name
