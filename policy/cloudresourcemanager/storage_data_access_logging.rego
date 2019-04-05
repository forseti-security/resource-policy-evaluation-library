# Copyright 2019 The micromanager Authors. All rights reserved.
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


package gcp.cloudresourcemanager.projects.iam.policy.storage_data_access_logs

#####
# Resource metadata
#####

labels = input.settings.userLabels

#####
# Policy evaluation
#####

default valid=false


valid = true {

  # If all of these are satisified, storage data access logs are enabled
  input.auditConfigs[storage].service = "storage.googleapis.com"
  input.auditConfigs[storage].auditLogConfigs[_].logType = "ADMIN_READ"
  input.auditConfigs[storage].auditLogConfigs[_].logType = "DATA_WRITE"
  input.auditConfigs[storage].auditLogConfigs[_].logType = "DATA_READ"

}

#####
# Remediation
#####

# Copy the input, omit the auditConfigs
remediate[key] = value {
  key != "auditConfigs"
  input[key]=value
}

# Add back the audit configs by combining all non-storage configs with a statically defined storage audit config
remediate[key] = value {
  key:="auditConfigs"
  array.concat(_storageAuditConfig, _otherAuditConfigs, _auditConfigs)
  value:=_auditConfigs
}

# The expected storage audit config
_storageAuditConfig = [{
  "service": "storage.googleapis.com",
  "auditLogConfigs": [
    {
      "logType": "ADMIN_READ"
    },
    {
      "logType": "DATA_WRITE"
    },
    {
      "logType": "DATA_READ"
    }
  ]
}]

# Non-storage audit configs from the input
_otherAuditConfigs = [ ac | ac := input.auditConfigs[_]
  ac.service != "storage.googleapis.com"
]
