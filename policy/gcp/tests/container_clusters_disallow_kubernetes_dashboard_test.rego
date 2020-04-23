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

package rpe.policy.container_clusters_disallow_kubernetes_dashboard

test_compliant_policies {
	compliant with input.resource as {
		"labels": {},
		"addonsConfig": {"kubernetesDashboard": {"disabled": true}},
	}
}

test_noncompliant_policies {
	not compliant with input.resource as {
		"labels": {},
		"addonsConfig": {"kubernetesDashboard": {"disabled": false}},
	}
}

test_exclusion_labels {
	excluded with input as {"resource": {"labels": {
		"exclude-me": "true",
		"environment": "bar",
	}}}
		 with data.config.exclusions.labels as {"exclude-me": "true"}
}

test_exclusion_no_labels {
	not excluded with input as {"resource": {}}
		 with data.config.exclusions.labels as {"exclude-me": "true"}
}

test_no_exclusion_labels {
	not excluded with input as {"resource": {"labels": {"environment": "foo"}}}
		 with data.config.exclusions.labels as {"exclude-me": "true"}
}
