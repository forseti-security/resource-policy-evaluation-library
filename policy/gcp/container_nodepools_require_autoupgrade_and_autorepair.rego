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

package rpe.policy.container_nodepools_require_autoupgrade_and_autorepair

#####
# Policy metadata
#####

description = "Require that nodepools have auto-upgrade and auto-repair enabled"

applies_to = ["container.googleapis.com/NodePool"]

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

compliant {
	resource.management.autoRepair == true
	resource.management.autoUpgrade == true
}

excluded {
	data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

remediate = {
	"_remediation_spec": "v2beta1",
	"steps": [enable_node_auto_repair_upgrade],
}

enable_node_auto_repair_upgrade = {
	"method": "setManagement",
	"params": {
		"name": combinedName,
		"body": {
			"name": combinedName,
			"management": {
				"autoRepair": true,
				"autoUpgrade": true,
			},
		},
	},
}

# break out the selfLink so we can extract the project, region, cluster and name
selfLinkParts = split(resource.selfLink, "/")

# create combined resource name
combinedName = sprintf("projects/%s/locations/%s/clusters/%s/nodePools/%s", [selfLinkParts[5], selfLinkParts[7], selfLinkParts[9], selfLinkParts[11]])
