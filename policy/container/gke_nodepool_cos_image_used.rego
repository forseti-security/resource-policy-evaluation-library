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


package gcp.container.projects.locations.clusters.nodePools.policy.cos_image_used

#####
# Resource metadata
#####

labels = input.labels

#####
# Policy evaluation
#####

default valid = false

# Check if COS image is being used
valid = true {
  input.config.imageType == "COS"
}

# Check for a global exclusion based on resource labels
valid = true {
  data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

# remediate[key] = value {
#  key != "config"
#  input[key]=value
# }

# remediate[key] = value {
#  key := "config"
#  value := _config
# }

# _config[key]=value{
#   key != "imageType"
#   input.config[key]=value
# }

# _config[key]=value{
#   key := "imageType"
#   value := "COS"
# }


remediate = {
  "_remediation_spec": "v2beta1",
  "steps": [
    use_cos_image
  ]
}

use_cos_image = {
    "method": "update",
    "params": {
        "name": combinedName,
        "body": {
          "imageType": "COS"
        }
    }
}

# break out the selfLink so we can extract the project, region, cluster and name
selfLinkParts = split(input.selfLink, "/")

# create combined resource name
combinedName = sprintf("projects/%s/locations/%s/clusters/%s/nodePools/%s", [selfLinkParts[5], selfLinkParts[7], selfLinkParts[9], selfLinkParts[11]])