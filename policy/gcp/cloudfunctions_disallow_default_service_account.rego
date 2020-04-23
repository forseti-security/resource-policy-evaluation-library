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

package rpe.policy.cloudfunctions_disallow_default_service_account

#####
# Policy metadata
#####

description = "Disallow the use of the default service account for running cloud functions"

applies_to = ["cloudfunctions.googleapis.com/CloudFunction"]

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

# Check if default service account is not used
compliant {
	resource.serviceAccountEmail != serviceAccountEmail
}

# Check for a global exclusion based on resource labels
excluded {
	data.exclusions.label_exclude(labels)
}

# extract project name from function name
projectNamePart = split(resource.name, "/")

# construct email for default cloud function service account
serviceAccountEmail = concat("@", [projectNamePart[1], "appspot.gserviceaccount.com"])
