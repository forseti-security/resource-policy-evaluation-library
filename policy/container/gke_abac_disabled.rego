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


package gcp.container.projects.locations.clusters.policy.abac_disabled

#####
# Resource metadata
#####

labels = input.labels

#####
# Policy evaluation
#####

default valid = false

# Check if legacy ABAC is enabled
valid = true {
  input.legacyAbac.enabled == false
}

# Check for a global exclusion based on resource labels
valid = true {
  data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

remediate = {
  "_remediation_spec": "v2beta1",
  "steps": [
    enable_legacy_abac
  ]
}

enable_legacy_abac = {
    "method": "setLegacyAbac",
    "params": {
        "name": combinedName,
        "body":  {
            "name": combinedName,
            "enabled": false
        }
    }
}

# break out the selfLink so we can extract the project, region and name
selfLinkParts = split(input.selfLink, "/")

# create combined resource name
combinedName = sprintf("projects/%s/locations/%s/clusters/%s", [selfLinkParts[5], selfLinkParts[7], selfLinkParts[9]])