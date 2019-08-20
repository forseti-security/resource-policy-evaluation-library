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

package gcp.appengine.apps.services.versions.instances.policy.debug

#####
# Resource metadata
#####

labels = input.labels

#####
# Policy evaluation
#####

default valid = true

valid = false {
    input.vmDebugEnabled == true
}


#####
 # Remediation
 #####

  # Since we cannot remediate it, debug mode is read-only and its on the instance. Lets end it with "No possible remediation"
 remediate[key] = value {
   input.vmDebugEnabled == false
   input[key]=value
 }