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

package rpe.policy.cloudresourcemanager_projects_require_all_audit_logs

#####
# Policy metadata
#####

description = "Require that all audit logs are enabled on a project"

applies_to = ["cloudresourcemanager.googleapis.com/Project"]

#####
# Resource metadata
#####

resource = input.resource

iam = input.iam

labels = resource.settings.userLabels

#####
# Policy evaluation
#####

default compliant = false

default excluded = false

compliant {
	# If there is only 1 auditConfig entry, and it enables all logs for allServices, this requirement is met
	count(iam.auditConfigs) = 1
	iam.auditConfigs[entry].service = "allServices"
	iam.auditConfigs[entry].auditLogConfigs[_].logType = "ADMIN_READ"
	iam.auditConfigs[entry].auditLogConfigs[_].logType = "DATA_WRITE"
	iam.auditConfigs[entry].auditLogConfigs[_].logType = "DATA_READ"
}

excluded {
	data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

remediate = {
	"_remediation_spec": "v2beta1",
	"steps": [set_audit_configs],
}

set_audit_configs = {
	"method": "setIamPolicy",
	"params": {
		"resource": resource.projectId,
		"body": {
			"policy": {"audit_configs": _defaultAuditConfig},
			"updateMask": "auditConfigs",
		},
	},
}

# The expected default audit config
_defaultAuditConfig = [{
	"service": "allServices",
	"audit_log_configs": [
		{"log_type": "ADMIN_READ"},
		{"log_type": "DATA_WRITE"},
		{"log_type": "DATA_READ"},
	],
}]
