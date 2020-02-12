# Copyright 2020 The resource-policy-evaluation-library Authors. All rights reserved.
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

client_kwargs = {
    'credentials': Credentials(token='')
}

CaiTestCase = collections.namedtuple('CaiTestCase', 'data content_type resource_cls')

test_cases = [
    CaiTestCase(
        data={
            "name": "//appengine.googleapis.com/apps/test-project/services/default/versions/1234567890/instances/test-instance",
            "asset_type": "appengine.googleapis.com/Instance",
        },
        content_type="resource",
        resource_cls=GcpAppEngineInstance
    ),
    CaiTestCase(
        data={
            "name": "//bigquery.googleapis.com/projects/test-project/datasets/test-resource",
            "asset_type": "bigquery.googleapis.com/Dataset",
        },
        content_type="resource",
        resource_cls=GcpBigqueryDataset
    ),
    CaiTestCase(
        data={
            "name": "//bigtable.googleapis.com/projects/test-project/instances/test-resource",
            "asset_type": "bigtableadmin.googleapis.com/Instance",
        },
        content_type="resource",
        resource_cls=GcpBigtableInstance
    ),
    CaiTestCase(
        data={
            "name": "//bigtable.googleapis.com/projects/test-project/instances/test-resource",
            "asset_type": "bigtableadmin.googleapis.com/Instance",
        },
        content_type="iam",
        resource_cls=GcpBigtableInstanceIam
    ),
    CaiTestCase(
        data={
            "name": "//cloudfunctions.googleapis.com/projects/test-project/locations/us-central1/functions/my-function",
            "asset_type": "cloudfunctions.googleapis.com/CloudFunction",
        },
        content_type="resource",
        resource_cls=GcpCloudFunction
    ),
    CaiTestCase(
        data={
            "name": "//cloudfunctions.googleapis.com/projects/test-project/locations/us-central1/functions/my-function",
            "asset_type": "cloudfunctions.googleapis.com/CloudFunction",
        },
        content_type="iam",
        resource_cls=GcpCloudFunctionIam
    ),
    CaiTestCase(
        data={
            "name": "//compute.googleapis.com/projects/test-project/zones/us-central1-a/instances/test-resource",
            "asset_type": "compute.googleapis.com/Instance",
        },
        content_type="resource",
        resource_cls=GcpComputeInstance
    ),
    CaiTestCase(
        data={
            "name": "//compute.googleapis.com/projects/test-project/zones/us-central1-a/disks/test-resource",
            "asset_type": "compute.googleapis.com/Disk",
        },
        content_type="resource",
        resource_cls=GcpComputeDisks
    ),
    CaiTestCase(
        data={
            "name": "//compute.googleapis.com/projects/test-project/regions/asia-east2/subnetworks/test-resource",
            "asset_type": "compute.googleapis.com/Subnetwork",
        },
        content_type="resource",
        resource_cls=GcpComputeSubnetwork
    ),
    CaiTestCase(
        data={
            "name": "//compute.googleapis.com/projects/test-project/global/firewalls/test-resource",
            "asset_type": "compute.googleapis.com/Firewall",
        },
        content_type="resource",
        resource_cls=GcpComputeFirewall
    ),
    CaiTestCase(
        data={
            "name": "//dataproc.googleapis.com/projects/test-project/regions/us-central1/clusters/test-resource",
            "asset_type": "dataproc.googleapis.com/Cluster",
        },
        content_type="resource",
        resource_cls=GcpDataprocCluster
    ),
    CaiTestCase(
        data={
            "name": "//container.googleapis.com/projects/test-project/locations/us-central1/clusters/test-resource",
            "asset_type": "container.googleapis.com/Cluster",
        },
        content_type="resource",
        resource_cls=GcpGkeCluster
    ),
    CaiTestCase(
        data={
            "name": "//container.googleapis.com/projects/test-project/locations/us-central1/clusters/foofoo123/nodePools/test-resource",
            "asset_type": "container.googleapis.com/NodePool",
        },
        content_type="resource",
        resource_cls=GcpGkeClusterNodepool
    ),
    CaiTestCase(
        data={
            "name": "//pubsub.googleapis.com/projects/test-project/subscriptions/test-resource",
            "asset_type": "pubsub.googleapis.com/Subscription",
        },
        content_type="resource",
        resource_cls=GcpPubsubSubscription
    ),
    CaiTestCase(
        data={
            "name": "//pubsub.googleapis.com/projects/test-project/subscriptions/test-resource",
            "asset_type": "pubsub.googleapis.com/Subscription",
        },
        content_type="iam",
        resource_cls=GcpPubsubSubscriptionIam
    ),
    CaiTestCase(
        data={
            "name": "//pubsub.googleapis.com/projects/test-project/topics/test-resource",
            "asset_type": "pubsub.googleapis.com/Topic",
        },
        content_type="resource",
        resource_cls=GcpPubsubTopic
    ),
    CaiTestCase(
        data={
            "name": "//pubsub.googleapis.com/projects/test-project/topics/test-resource",
            "asset_type": "pubsub.googleapis.com/Topic",
        },
        content_type="iam",
        resource_cls=GcpPubsubTopicIam
    ),
    CaiTestCase(
        data={
            "name": "//storage.googleapis.com/test-resource",
            "asset_type": "storage.googleapis.com/Bucket",
        },
        content_type="resource",
        resource_cls=GcpStorageBucket
    ),
    CaiTestCase(
        data={
            "name": "//storage.googleapis.com/test-resource",
            "asset_type": "storage.googleapis.com/Bucket",
        },
        content_type="iam",
        resource_cls=GcpStorageBucketIamPolicy
    ),
    CaiTestCase(
        data={
            "name": "//cloudsql.googleapis.com/projects/test-project/instances/test-resource",
            "asset_type": "sqladmin.googleapis.com/Instance",
        },
        content_type="resource",
        resource_cls=GcpSqlInstance
    ),
    CaiTestCase(
        data={
            "name": "//cloudresourcemanager.googleapis.com/projects/test-resource",
            "asset_type": "cloudresourcemanager.googleapis.com/Project",
        },
        content_type="resource",
        resource_cls=GcpProject
    ),
    CaiTestCase(
        data={
            "name": "//cloudresourcemanager.googleapis.com/projects/test-resource",
            "asset_type": "cloudresourcemanager.googleapis.com/Project",
        },
        content_type="iam",
        resource_cls=GcpProjectIam
    ),
    CaiTestCase(
        data={
            "name": "//serviceusage.googleapis.com/projects/179590471157/services/test-resource",
            "asset_type": "serviceusage.googleapis.com/Service",
        },
        content_type="resource",
        resource_cls=GcpProjectService
    ),
]


@pytest.mark.parametrize(
    "case",
    test_cases,
    ids=[case.resource_cls.__name__ for case in test_cases])
def test_gcp_resource_from_cai_data(case):
    r = GoogleAPIResource.from_cai_data(
        case.data.get('name'),
        case.data.get('asset_type'),
        case.content_type,
        client_kwargs=client_kwargs,
    )
    assert r.__class__ == case.resource_cls
    assert r.full_resource_name() == case.data.get('name')


def test_bad_content_type():

    with pytest.raises(ResourceException) as excinfo:
        GoogleAPIResource.from_cai_data(
            '//cloudresourcemanager.googleapis.com/projects/test-resource',
            'cloudresourcemanager.googleapis.com/Project',
            'fake_content_type',
            client_kwargs=client_kwargs,
        )

    assert 'Unrecognized content type' in str(excinfo.value)


def test_bad_asset_type():

    with pytest.raises(ResourceException) as excinfo:
        GoogleAPIResource.from_cai_data(
            '//cloudfakeservice.googleapis.com/widgets/test-resource',
            'cloudfakeservice.googleapis.com/Widget',
            client_kwargs=client_kwargs,
        )

    assert 'Unrecognized asset type' in str(excinfo.value)
