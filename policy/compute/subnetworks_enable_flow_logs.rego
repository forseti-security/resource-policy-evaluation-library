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


package gcp.compute.subnetworks.policy.enable_flow_logs

#####
# Resource metadata
#####

labels = input.labels

#####
# Policy evaluation
#####

default valid = false

# Check if flow logs are enabled
valid = true {
  input.enableFlowLogs == true
}

# Check for a global exclusion based on resource labels
valid = true {
  data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

# Make a copy of the input, omitting the enableFlowLogs
remediate[key] = value {
  key != "enableFlowLogs"
  input[key]=value
}

# Set the enableFlowLogs field such that the subnetwork adheres to the policy
remediate[key] = value {
  key := "enableFlowLogs"
  value := true
}
