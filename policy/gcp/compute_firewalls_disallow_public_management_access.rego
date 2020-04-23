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

package rpe.policy.compute_firewalls_disallow_public_management_access

import data.rpe.gcp.util as gcputil

#####
# Policy metadata
#####

description = "Disallow public management access in firewall rules"

applies_to = ["compute.googleapis.com/Firewall"]

#####
# Resource metadata
#####

resource = input.resource

labels = resource.labels

# A list of TCP ports we don't want to allow public access to
bad_tcp_ports = [22, 3389]

#####
# Policy evaluation
#####

default compliant = true

default excluded = false

# Check if public access is enabled for everything
compliant = false {
	resource.direction == "INGRESS"
	resource.sourceRanges[_] == "0.0.0.0/0"
	resource.allowed[rule_id].IPProtocol == "all"
	not resource.disabled
}

# Check if public access is enabled for a bad TCP port
compliant = false {
	resource.direction == "INGRESS"
	resource.sourceRanges[_] == "0.0.0.0/0"
	has_bad_tcp_port
	not resource.disabled
}

# Check for bad TCP ports in rules
default has_bad_tcp_port = false

## Explicitly lists bad port
has_bad_tcp_port {
	resource.allowed[rule_id].IPProtocol == "tcp"
	resource.allowed[rule_id].ports[_] == sprintf("%d", [bad_tcp_ports[_]])
}

## Allows all ports
has_bad_tcp_port {
	resource.allowed[rule_id].IPProtocol == "tcp"
	not resource.allowed[rule_id].ports
}

## Has a port range that contains a bad port
has_bad_tcp_port {
	resource.allowed[rule_id].IPProtocol == "tcp"
	contains(resource.allowed[rule_id].ports[port], "-")
	port_range := split(resource.allowed[rule_id].ports[port], "-")
	to_number(port_range[0]) <= bad_tcp_ports[port_id]
	to_number(port_range[1]) >= bad_tcp_ports[port_id]
}

#####
# Remediation
#####

remediate = {
	"_remediation_spec": "v2beta1",
	"steps": [disable_firewall],
}

disable_firewall = {
	"method": "patch",
	"params": {
		"project": gcputil.resource_from_collection_path(resource.selfLink, "projects"),
		"firewall": resource.name,
		"body": {"disabled": true},
	},
}
