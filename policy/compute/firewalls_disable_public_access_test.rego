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


package gcp.compute.firewalls.policy.disable_public_access

test_good_firewall {
  valid with input as {
      "sourceRanges": [
        "203.0.113.0/29"
      ],
      "allowed": [
        {
        "IPProtocol": "tcp"
      }
    ]
  }
}

test_good_firewall_disabled {
  valid with input as {
    "sourceRanges": [
      "203.0.113.0/29"
    ],
    "allowed": [
        {
        "IPProtocol": "tcp"
      }
    ],
    "disabled": "true"
  }
}

test_bad_firewall {
  not valid with input as {
      "sourceRanges": [
        "0.0.0.0/0"
      ],
      "allowed": [
        {
        "IPProtocol": "tcp"
      }
    ]
  }
}

test_bad_firewall_disabled {
   valid with input as {
    "sourceRanges": [
      "0.0.0.0/0"
    ],
    "allowed": [
        {
        "IPProtocol": "tcp"
      }
    ],
    "disabled": "true"
  }
}
