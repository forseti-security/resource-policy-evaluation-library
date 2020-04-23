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

package rpe.policy.appengine_instances_disallow_debug_mode

#####
# Policy metadata
#####

description = "Disallow the use of debug mode on AppEngine Flex instances"

applies_to = ["appengine.googleapis.com/Instance"]

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
	resource.vmDebugEnabled == true
}

#####
# Remediation
#####

remediate = {
	"_remediation_spec": "v2beta1",
	"steps": [delete_instance],
}

delete_instance = {
	"method": "delete",
	"params": {
		"appsId": name_parts[1],
		"servicesId": name_parts[3],
		"versionsId": name_parts[5],
		"instancesId": name_parts[7],
	},
}

name_parts = split(resource.name, "/")
