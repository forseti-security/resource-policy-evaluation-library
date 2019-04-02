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


package gcp.sqladmin.instances.policy.backups

test_enabled {
  valid with input as {
     "settings": {
        "backupConfiguration": {
           "enabled": true
        },
        "userLabels": {
        }
     }
  }
}

test_enabled_with_override {
  valid with input as {
     "settings": {
        "backupConfiguration": {
           "enabled": true
        },
        "userLabels": {
           "forseti-enforcer": "disable"
        }
     }
  }
}

test_enabled_missing_labels {
  valid with input as {
     "settings": {
        "backupConfiguration": {
           "enabled": true
        }
     }
  }
}

test_disabled {
  not valid with input as {
     "settings": {
        "backupConfiguration": {
           "enabled": false
        },
        "userLabels": {
        }
     }
  }
}

test_disabled_with_override {
  valid with input as {
     "settings": {
        "backupConfiguration": {
           "enabled": false
        },
        "userLabels": {
           "forseti-enforcer": "disable"
        }
     }
  }
}

test_disabled_missing_labels {
  not valid with input as {
     "settings": {
        "backupConfiguration": {
           "enabled": false
        }
     }
  }
}
