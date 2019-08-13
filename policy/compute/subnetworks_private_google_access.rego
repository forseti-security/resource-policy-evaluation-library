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


package gcp.compute.subnetworks.policy.private_google_access

#####
# Resource metadata
#####

labels = input.labels

#####
# Policy evaluation
#####

default valid = false

# Check if accessing Google services without external IP is enabled
valid = true {
  input.privateIpGoogleAccess == true
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
    enable_private_google_access
  ]
}

enable_private_google_access = {
    "method": "setPrivateIpGoogleAccess",
    "params": {
        "subnetwork": input.name,
        "region": selfLinkParts[8],
        "project": selfLinkParts[6],
        "body":  {
            "privateIpGoogleAccess": true
        }
    }
}

# break out the selfLink so we can extract the project and region
selfLinkParts = split(input.selfLink, "/")