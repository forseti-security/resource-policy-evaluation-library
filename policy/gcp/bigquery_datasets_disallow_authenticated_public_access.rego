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

package rpe.policy.bigquery_datasets_disallow_authenticated_public_access

#####
# Policy metadata
#####

description = "Disallow authenticated public access to bigquery datasets"

applies_to = ["bigquery.googleapis.com/Dataset"]

#####
# Resource metadata
#####

resource = input.resource

labels = resource.labels

#####
# Policy evaluation
#####

default compliant = true

default excluded = false

compliant = false {
	# Check for bad acl
	resource.access[_].specialGroup == "allAuthenticatedUsers"
}

excluded {
	data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

remediate = {
	"_remediation_spec": "v2beta1",
	"steps": [remove_bad_bindings],
}

remove_bad_bindings = {
	"method": "patch",
	"params": {
		"projectId": resource.datasetReference.projectId,
		"datasetId": resource.datasetReference.datasetId,
		"body": {"access": _access},
	},
}

# Return only compliant acls using the function below
_access = [acl |
	acl := resource.access[_]
	_compliant_acl(acl)
]

_compliant_acl(acl) {
	# If the specialGroup is anything other than "allAuthenticatedUsers"
	acl.specialGroup != "allAuthenticatedUsers"
}

_compliant_acl(acl) {
	# Or if there is no specialGroup key
	not acl.specialGroup
}
