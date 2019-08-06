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


package gcp.compute.subnetworks.privateip.policy.private_ip_google_access

test_valid_policies {
  valid with input as {
     "labels": {
     },
     "privateIpGoogleAccess": true
  }
}

test_valid_policies_with_override {
  valid with input as {
     "labels": {
        "forseti-enforcer": "disable",
     },
     "privateIpGoogleAccess": true
  }
}

test_valid_policies_missing_labels {
  valid with input as {
     "privateIpGoogleAccess": true
  }
}

test_invalid_policies {
  not valid with input as {
     "labels": {
     },
     "privateIpGoogleAccess": false
  }
}

test_invalid_policies_with_override {
  valid with input as {
     "labels": {
        "forseti-enforcer": "disable",
     },
     "privateIpGoogleAccess": false
  }
}

test_invalid_policies_missing_labels {
  not valid with input as {
     "privateIpGoogleAccess": false
  }
}
