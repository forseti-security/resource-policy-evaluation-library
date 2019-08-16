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


package gcp.container.projects.locations.clusters.nodePools.policy.auto_repair_upgrade_enabled

test_valid_policies {
  valid with input as {
    "labels": {
    },
    "management": {
      "autoRepair": true,
      "autoUpgrade": true
    }
  }
}

test_valid_policies_with_override {
  valid with input as {
    "labels": {
      "forseti-enforcer": "disable",
    },
    "management": {
      "autoRepair": true,
      "autoUpgrade": true
    }
  }
}

test_valid_policies_missing_labels {
  valid with input as {
    "management": {
      "autoRepair": true,
      "autoUpgrade": true
    }
  }
}

test_invalid_policies {
  not valid with input as {
    "labels": {
    },
    "management": {
      "autoRepair": false,
      "autoUpgrade": false
    }
  }
}

test_invalid_policies_with_override {
  valid with input as {
    "labels": {
      "forseti-enforcer": "disable",
    },
    "management": {
      "autoRepair": false,
      "autoUpgrade": false
    }
  }
}

test_invalid_policies_missing_labels {
  not valid with input as {
    "management": {
      "autoRepair": false,
      "autoUpgrade": false
    }
  }
}