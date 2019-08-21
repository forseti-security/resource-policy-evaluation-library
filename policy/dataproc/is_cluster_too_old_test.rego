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


package gcp.dataproc.projects.regions.clusters.policy.is_cluster_too_old

#as validness depends on time of execution, we can surely test only part with labels
test_invalid_policies {
  not valid with input as {
   "labels": {
   },
   "config": {
     "statusHistory": [
       {"state": "begin",
        "stateStartTime": "2017-01-01T01:00:00.000Z"},
       {"state": "updated",
        "stateStartTime": "2021-11-11T11:11:11.111Z"}
     ]
   }
  }
}

test_invalid_policies_with_override {
  valid with input as {
     "labels": {
        "forseti-enforcer": "disable",
     },
     "config": {
       "statusHistory": [
         {"state": "begin",
          "stateStartTime": "2017-01-01T01:00:00.000Z"},
         {"state": "updated",
          "stateStartTime": "2021-11-11T11:11:11.111Z"}
       ]
     }
  }
}
