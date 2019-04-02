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


package gcp.sqladmin.instances.policy.acl

test_good_acls {
  valid with input as {
     "settings": {
        "ipConfiguration": {
           "authorizedNetworks": [
              {
                 "value": "203.0.113.0/29",
              }
           ]
        },
        "userLabels": {
        }
     }
  }
}

test_good_acls_with_override {
  valid with input as {
     "settings": {
        "ipConfiguration": {
           "authorizedNetworks": [
              {
                 "value": "203.0.113.0/29",
              }
           ]
        },
        "userLabels": {
           "forseti-enforcer": "disable"
        }
     }
  }
}

test_good_acls_missing_labels {
  valid with input as {
     "settings": {
        "ipConfiguration": {
           "authorizedNetworks": [
              {
                 "value": "203.0.113.0/29",
              }
           ]
        }
     }
  }
}

test_bad_acl {
  not valid with input as {
     "settings": {
        "ipConfiguration": {
           "authorizedNetworks": [
              {
                 "value": "0.0.0.0/0",
              }
           ]
        },
        "userLabels": {
        }
     }
  }
}

test_bad_acl_with_override {
  valid with input as {
     "settings": {
        "ipConfiguration": {
           "authorizedNetworks": [
              {
                 "value": "0.0.0.0/0",
              }
           ]
        },
        "userLabels": {
           "forseti-enforcer": "disable"
        }
     }
  }
}

test_bad_acl_missing_labels {
  not valid with input as {
     "settings": {
        "ipConfiguration": {
           "authorizedNetworks": [
              {
                 "value": "0.0.0.0/0",
              }
           ]
        }
     }
  }
}

