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

package rpe.policy.storage_buckets_require_object_versioning

#####
# Policy metadata
#####

description = "Require object versioning for storage buckets"

applies_to = ["storage.googleapis.com/Bucket"]

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
	resource.versioning.enabled = true
}

excluded {
	data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

remediate = {
	"_remediation_spec": "v2beta1",
	"steps": [enable_versioning],
}

enable_versioning = {
	"method": "patch",
	"params": {
		"bucket": resource.name,
		"body": {"versioning": {"enabled": true}},
	},
}
