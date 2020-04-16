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

package rpe.policy.compute_disks_disallow_unapproved_images

#####
# Policy metadata
#####

description = "Disallow use of unapproved images for compute disks"

applies_to = ["compute.googleapis.com/Disk"]

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

# approved project_id for images is configured in policy/config.yaml - instances.harden_images_project

# Check if hardened image used
compliant {
	contains(resource.sourceImage, concat("/", ["projects", data.config.gcp.compute.harden_images_project]))
}

excluded {
	data.exclusions.label_exclude(labels)
}
