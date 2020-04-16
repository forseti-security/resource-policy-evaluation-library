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

package rpe.policy.container_nodepools_require_cos_image

#####
# Policy metadata
#####

description = "Require nodepools to use the Container-Optimized OS images"

applies_to = ["container.googleapis.com/Cluster"]

#####
# Resource metadata
#####

resource = input.resource

labels = resource.labels

#####
# Policy evaluation
#####

default compliant = false

default excluded = false

# Check if COS image is being used
compliant {
	count(_noncompliant_nodepools) == 0
}

# Check for a global exclusion based on resource labels
excluded {
	data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

remediate = {
	"_remediation_spec": "v2beta1",
	"steps": use_cos_image,
}

# iterate steps over noncompliant nodePools (can be updated one at a time)
use_cos_image = result {
	result := {combined | combined := {
		"method": "update",
		"params": {
			"name": combinedName,
			"body": {"update": {
				"desiredNodePoolId": _noncompliant_nodepools[_],
				"desiredImageType": "COS",
			}},
		},
	}}
}

_allowed_image_types = {"COS", "COS_CONTAINERD"}

_all_nodepools = {name |
	name := resource.nodePools[_].name
}

_compliant_nodepools = {name |
	resource.nodePools[p].config.imageType = _allowed_image_types[_]
	name := resource.nodePools[p].name
}

_noncompliant_nodepools = _all_nodepools - _compliant_nodepools

# break out the selfLink so we can extract the project, region, cluster and name
selfLinkParts = split(resource.selfLink, "/")

# create combined resource name
combinedName = sprintf("projects/%s/locations/%s/clusters/%s", [selfLinkParts[5], selfLinkParts[7], selfLinkParts[9]])
