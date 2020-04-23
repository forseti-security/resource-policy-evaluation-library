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

package rpe

import data.rpe.util as util

policies = [{
	"policy_id": name,
	"description": object.get(p, "description", ""),
	"applies_to": p.applies_to,
} |
	p = data.rpe.policy[name]
]

evaluate = [{
	"policy_id": name,
	"compliant": object.get(data.rpe.policy[name], "compliant", false),
	"excluded": object.get(data.rpe.policy[name], "excluded", false),
	"remediable": util.has_field(data.rpe.policy[name], "remediate"),
} |
	name := matched_policies[_]
]

matched_policies = sort([name |
	p = data.rpe.policy[name]
	input.type == p.applies_to[_]
])
