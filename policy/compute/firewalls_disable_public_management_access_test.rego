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

test_good_firewall_1 {
	valid with input as {
		"direction": "INGRESS",
		"sourceRanges": ["203.0.113.0/29"],
		"allowed": [{"IPProtocol": "tcp"}],
	}
}

test_good_firewall_2 {
	valid with input as {
		"direction": "INGRESS",
		"sourceRanges": ["203.0.113.0/29"],
		"allowed": [{
			"IPProtocol": "tcp",
			"ports": ["22"],
		}],
	}
}

test_good_firewall_disabled_1 {
	valid with input as {
		"direction": "INGRESS",
		"sourceRanges": ["203.0.113.0/29"],
		"allowed": [{"IPProtocol": "tcp"}],
		"disabled": "true",
	}
}

test_good_firewall_disabled_2 {
	valid with input as {
		"direction": "INGRESS",
		"sourceRanges": ["0.0.0.0/0"],
		"allowed": [{
			"IPProtocol": "tcp",
			"ports": ["22"],
		}],
		"disabled": "true",
	}
}

test_bad_firewall_all {
	not valid with input as {
		"direction": "INGRESS",
		"sourceRanges": ["0.0.0.0/0"],
		"allowed": [{"IPProtocol": "all"}],
	}
}

test_bad_firewall_tcp {
	not valid with input as {
		"direction": "INGRESS",
		"sourceRanges": ["0.0.0.0/0"],
		"allowed": [{"IPProtocol": "tcp"}],
	}
}

test_bad_firewall_ssh {
	not valid with input as {
		"direction": "INGRESS",
		"sourceRanges": ["0.0.0.0/0"],
		"allowed": [{
			"IPProtocol": "tcp",
			"ports": ["22"],
		}],
	}
}

test_bad_firewall_rdp {
	not valid with input as {
		"direction": "INGRESS",
		"sourceRanges": ["0.0.0.0/0"],
		"allowed": [{
			"IPProtocol": "tcp",
			"ports": ["3389"],
		}],
	}
}

test_bad_firewall_ssh_in_range {
	not valid with input as {
		"direction": "INGRESS",
		"sourceRanges": ["0.0.0.0/0"],
		"allowed": [{
			"IPProtocol": "tcp",
			"ports": ["20-25"],
		}],
	}
}

test_bad_firewall_rdp_in_range {
	not valid with input as {
		"direction": "INGRESS",
		"sourceRanges": ["0.0.0.0/0"],
		"allowed": [{
			"IPProtocol": "tcp",
			"ports": ["3380-3600"],
		}],
	}
}
