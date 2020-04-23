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

package rpe.policy.sql_instances_require_backup_configuration

#####
# Policy metadata
#####

description = "Require scheduled backups for SQL instances"

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

# Check if backups are enabled
compliant {
	resource.settings.backupConfiguration.enabled == true
}

# If this is a replica, you can't enable backups
compliant {
	resource.replicaConfiguration
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
	"steps": [enable_backups],
}

enable_backups = {
	"method": "patch",
	"params": {
		"project": resource.project,
		"instance": resource.name,
		"body": {"settings": {"backupConfiguration": {"enabled": true}}},
	},
}
