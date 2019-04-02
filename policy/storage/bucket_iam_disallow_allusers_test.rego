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


package gcp.storage.buckets.iam.policy.disallow_allusers

test_valid_policies {
  valid with input as {
   "bindings": [
      {
         "role": "roles/storage.legacyBucketReader",
         "members": [
            "your_user@your_org.tld"
         ]
      }
    ],
   "_resource": {
      "labels": {
      }
    }
  }
}

test_valid_policies_with_override {
  valid with input as {
   "bindings": [
      {
         "role": "roles/storage.legacyBucketReader",
         "members": [
            "your_user@your_org.tld"
         ]
      }
   ],
   "_resource": {
      "labels": {
         "forseti-enforcer": "disable"
      }
    }
  }
}

test_valid_policies_missing_labels {
  valid with input as {
   "bindings": [
      {
         "role": "roles/storage.legacyBucketReader",
         "members": [
            "your_user@your_org.tld"
         ]
      }
   ]
  }
}

test_invalid_policies {
  not valid with input as {
   "bindings": [
      {
         "role": "roles/storage.legacyBucketReader",
         "members": [
            "allUsers"
         ]
      }
    ],
   "_resource": {
      "labels": {
      }
    }
  }
}

test_invalid_policies_with_override {
  valid with input as {
   "bindings": [
      {
         "role": "roles/storage.legacyBucketReader",
         "members": [
            "your_user@your_org.tld",
            "allUsers"
         ]
      }
   ],
   "_resource": {
      "labels": {
         "forseti-enforcer": "disable"
      }
    }
  }
}

test_invalid_policies_missing_labels {
  not valid with input as {
   "bindings": [
      {
         "role": "roles/storage.legacyBucketReader",
         "members": [
            "your_user@your_org.tld",
            "allUsers"
         ]
      }
   ]
  }
}
