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

package rpe.policy.container_clusters_disallow_legacy_abac

#####
# Policy metadata
#####

description = "Disallow the use of legacy abac for GKE clusters"

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

# Check if legacy ABAC is enabled
compliant {
	not resource.legacyAbac.enabled
}

excluded {
	data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

remediate = {
	"_remediation_spec": "v2beta1",
	"steps": [disable_legacy_abac],
}

disable_legacy_abac = {
	"method": "setLegacyAbac",
	"params": {
		"name": combinedName,
		"body": {
			"name": combinedName,
			"enabled": false,
		},
	},
}

# break out the selfLink so we can extract the project, region and name
selfLinkParts = split(resource.selfLink, "/")

# create combined resource name
combinedName = sprintf("projects/%s/locations/%s/clusters/%s", [selfLinkParts[5], selfLinkParts[7], selfLinkParts[9]])
