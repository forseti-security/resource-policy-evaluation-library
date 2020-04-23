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

package rpe.policy.sql_instances_require_ssl

#####
# Policy metadata
#####

description = "Require SSL for connectivity to SQL instances"

applies_to = ["sqladmin.googleapis.com/Instance"]

#####
# Resource metadata
#####

resource = input.resource

labels = resource.settings.userLabels

#####
# Policy evaluation
#####

default compliant = false

default excluded = false

# Check if non-ssl connections are allowed
compliant {
	resource.settings.ipConfiguration.requireSsl == true
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
	"steps": [set_require_ssl],
}

set_require_ssl = {
	"method": "patch",
	"params": {
		"project": resource.project,
		"instance": resource.name,
		"body": {"settings": {"ipConfiguration": {"requireSsl": true}}},
	},
}
