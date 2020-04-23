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

package rpe.policy.compute_firewalls_require_logging

import data.rpe.gcp.util as gcputil

#####
# Policy metadata
#####

description = "Require logging for firewall rules"

applies_to = ["compute.googleapis.com/Firewall"]

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

# Check if Logging is enabled
compliant {
	resource.logConfig.enable = true
}

# Check if firewall is disabled
compliant {
	resource.disabled
}

#####
# Remediation
#####

remediate = {
	"_remediation_spec": "v2beta1",
	"steps": [enable_logging],
}

enable_logging = {
	"method": "patch",
	"params": {
		"project": gcputil.resource_from_collection_path(resource.selfLink, "projects"),
		"firewall": resource.name,
		"body": {"logConfig": {"enable": true}},
	},
}
