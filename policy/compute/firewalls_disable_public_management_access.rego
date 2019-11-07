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

#####
# Resource metadata
#####

labels = input.labels

# A list of TCP ports we don't want to allow public access to
bad_tcp_ports = [22, 3389]

#####
# Policy evaluation
#####

default valid = true

# Check if public access is enabled for everything
valid = false {
  input.direction == "INGRESS"
  input.sourceRanges[_] == "0.0.0.0/0"
  input.allowed[rule_id].IPProtocol == "all"
  not input.disabled
}

# Check if public access is enabled for a bad TCP port
valid = false {
  input.direction == "INGRESS"
  input.sourceRanges[_] == "0.0.0.0/0"
  has_bad_tcp_port
  not input.disabled
}

# Check for bad TCP ports in rules
default has_bad_tcp_port = false

## Explicitly lists bad port
has_bad_tcp_port = true {
  input.allowed[rule_id].IPProtocol == "tcp"
  input.allowed[rule_id].ports[_] == sprintf("%d", [ bad_tcp_ports[_] ])
}

## Allows all ports
has_bad_tcp_port = true {
  input.allowed[rule_id].IPProtocol == "tcp"
  not input.allowed[rule_id].ports
}

## Has a port range that contains a bad port
has_bad_tcp_port = true {
  input.allowed[rule_id].IPProtocol == "tcp"
  contains(input.allowed[rule_id].ports[port], "-")
  port_range := split(input.allowed[rule_id].ports[port], "-")
  to_number(port_range[0]) <= bad_tcp_ports[port_id]
  to_number(port_range[1]) >= bad_tcp_ports[port_id]
}

#####
# Remediation
#####

# Make a copy of the input, omitting the versioning field
remediate[key] = value {
  key != "disabled"
  input[key]=value
}

# Set the versioning field such that the bucket adheres to the policy
remediate[key] = value {
  key:="disabled"
  value:="true"
}
