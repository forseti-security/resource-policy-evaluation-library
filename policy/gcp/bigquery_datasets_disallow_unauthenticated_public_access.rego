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


package rpe.policy.bigquery_datasets_disallow_unauthenticated_public_access

#####
# Policy metadata
#####

description = "Disallow unauthenticated public access to bigquery datasets"
applies_to =  [
  "bigquery.googleapis.com/Dataset"
]


#####
# Resource metadata
#####

resource = input.resource
labels = resource.labels

#####
# Policy evaluation
#####

default valid = true
default excluded = false

valid = false {
  # Check for bad acl
  resource.access[_].iamMember == "allUsers"
}

excluded = true {
  data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

remediate = {
  "_remediation_spec": "v2beta1",
  "steps": [
    remove_bad_bindings
  ]
}

remove_bad_bindings = {
    "method": "patch",
    "params": {
        "projectId": resource.datasetReference.projectId,
        "datasetId": resource.datasetReference.datasetId,
        "body": {
          "access": _access
        },
    }
}

# Return only valid acls using the function below
_access= [acl | acl := resource.access[_]
  _valid_acl(acl)
]

_valid_acl(acl) = true {
  # If the iamMember is anything other than "allUsers"
  acl.iamMember != "allUsers"
}{
  # Or if there is no iamMember key
  not acl["iamMember"]
}
