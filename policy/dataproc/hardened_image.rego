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


package gcp.dataproc.projects.regions.clusters.policy.hardened_image

#####
# Resource metadata
#####

labels = input.labels

#####
# Policy evaluation
#####

default valid = false

# approved project_id for images is configured in policy/config.yaml - dataproc:harden_images_project

# Check if hardened image used
valid = true {
    contains(input.config.masterConfig.imageUri, concat("/",["projects",data.config.dataproc.harden_images_project]))
}

# Check for a global exclusion based on resource labels
valid = true {
  data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

# Since we cannot remediate it, if policy fails lets end it with "No possible remediation"
remediate[key] = value {
  false
  input[key]=value
}
