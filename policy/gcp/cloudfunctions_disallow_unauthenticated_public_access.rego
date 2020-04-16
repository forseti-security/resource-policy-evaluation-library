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

package rpe.policy.cloudfunctions_disallow_unauthenticated_public_access

#####
# Policy metadata
#####

description = "Disallow unauthenticated public access for invoking cloud functions"

applies_to = ["cloudfunctions.googleapis.com/CloudFunction"]

#####
# Resource metadata
#####

resource = input.resource

iam = input.iam

labels = resource.labels

#####
# Policy evaluation
#####

default compliant = true

default excluded = false

compliant = false {
	iam.bindings[_].members[_] == "allUsers"
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
	"method": "setIamPolicy",
	"params": {
		"resource": resource.name,
		"body": {"policy": _policy},
	},
}

# Make a copy of the input, omitting the bindings
_policy[key] = value {
	key != "bindings"
	iam[key] = value
}

# Now rebuild the bindings
_policy[key] = value {
	key := "bindings"
	value := [binding |
		binding := _bindings[_]

		# Remove any binding that no longer have any members
		binding.members != []
	]
}

# Pass all binding through the fix_binding function
_bindings = [_fix_binding(binding) | binding := iam.bindings[_]]

# The fixed bindings are just the expected fields with members filtered
_fix_binding(b) = {"members": _remove_bad_members(b.members), "role": b.role}

# Given a list of members, remove the bad one(s)
_remove_bad_members(members) = m {
	m = [member |
		member := members[_]
		member != "allUsers"
	]
}
