# resource-policy-evaluation-library

The resource-policy-evaluation-library (rpe-lib) evaluates whether or not a given resource adheres to defined policies. It also attempts to remediate any policy violations.

[![Build Status](https://api.travis-ci.org/forseti-security/resource-policy-evaluation-library.svg?branch=master)](https://travis-ci.org/forseti-security/resource-policy-evaluation-library/)
[![PyPI version](https://badge.fury.io/py/rpe-lib.svg)](https://badge.fury.io/py/rpe-lib)

---

## Resources

The library works on `resources` and expects a fairly simple interface to any resource you wish to evaluate policy on. It expects an object with the following functions defined:

```
class MyResource:

    # Returns the body of a given resource as a dictionary
    def get(self):
        pass

    # Takes a remediation spec and attempts to remediate a resource
    def remediate(self, remediation):
        pass

    # Returns the resource type as a string
    #  Note: This should be a dotted-string that the engines will use to determine what policies are relevant
    type(self):
        pass
```

Some resources are provided with rpe-lib, and hopefully that will continue to grow, but it's not required that you use the provided resource classes.

## Adding resources and policies for evaluation

### Resources

The [resource-policy-evaluation-library](https://github.com/forseti-security/resource-policy-evaluation-library) 
(rpe-lib) utilizes the resources found in [rpe/resources/gcp.py](https://github.com/forseti-security/resource-policy-evaluation-library/blob/master/rpe/resources/gcp.py). 
For each resource, define a class object with the following functions defined, 
using the GCP API fields and methods for the resource. 
The base class for resources is [GoogleAPIResource](https://github.com/forseti-security/resource-policy-evaluation-library/blob/258fd3ab517597b4317bff2152357ed743ed6bc5/rpe/resources/gcp.py#L28).

Below is an example of a resource definition:

```
class GcpGkeClusterNodepool(GoogleAPIResource):

    service_name = "container"
    resource_path = "projects.locations.clusters.nodePools"
    version = "v1"
    readiness_key = 'status'
    readiness_value = 'RUNNING'

    required_resource_data = ['name', 'cluster', 'location', 'project_id']

    cai_type = "container.googleapis.com/NodePool"

    def _get_request_args(self):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}/nodePools/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['cluster'],
                self._resource_data['name']
            )
        }

    def _update_request_args(self, body):
        return {
            'name': 'projects/{}/locations/{}/clusters/{}/nodePools/{}'.format(
                self._resource_data['project_id'],
                self._resource_data['location'],
                self._resource_data['cluster'],
                self._resource_data['name']
            ),
            'body': body
        }
```

#### Resource Properties

##### Fields
- **cai_type (str)**: the CAI representation of resource type **(optional)**.
- **get_method (str)**: the API method to retrieve resource. **(Default = “get”)**
- **update_method (str)**: the API method to update resource. **(Default = “update”)**
- **service_name (str)**: the name of the API to call for the resource. 
  - E.g. `container.googleapis.com` becomes `container`
- **readiness_key (str)**: resource field key to check if readiness is defined. 
If a resource is not in a ready state, it cannot be updated. If the resource is 
retrieved and the state changes, updates to the resource will be rejected because 
the ETAG will have changed. Check for a readiness criteria if it exists for a 
resource and wait until the resource is in a ready state to return. **(Default = None)**
  - E.g. “status”
- **readiness_value (str)**: resource field value of the readiness_key that indicates ready state. **(Default = None)**
  - E.g. “RUNNING”
- **readiness_terminal_values (list str)**: resource field values that indicate 
a failed, suspended, or unknown state. Represented as a list of strings. **(Default = None)**
  - E.g. `['FAILED', 'MAINTENANCE', 'SUSPENDED', 'UNKNOWN_STATE']`
- **required_resource_data (list str)**: the fields that are required to be 
retrieved from the get_method for this resource to be parsed and updated. 
Represented as a list of strings. **(Default = [‘name’])**
  - E.g. `['name', 'cluster', 'location', 'project_id']`
- **resource_path (str)**: the REST resource
  - E.g. GKE NodePool resource_path would be `projects.locations.clusters.nodePools`: `https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1beta1/projects.locations.clusters.nodePools`
- **version (str)**: version of the API used.
  - E.g. “v1”, “v1beta”

##### Functions
- **_get_request_args()**: Uses the `get_method` of the defined resource to return a dictionary with the properties defined in the body.
- **_update_request_args()**: Uses the `update_method` of the defined resource to remediate/update the resource based on policy evaluation.

Once the resource class has been defined, add it to the `resource_type_map` 
dictionary in the `factory()` function in [rpe/resources/gcp.py](https://github.com/forseti-security/resource-policy-evaluation-library/blob/master/rpe/resources/gcp.py). 
with the `key: value` format as `service_name.resource_path: resource_class`. 
Using the example above, the `key: value` pair would be:
 
```
resource_type_map = {
	...
'container.projects.locations.clusters.nodePools': GcpGkeClusterNodepool,
...
}
```

### Engines

Policy evaluation/enforcement is handled by the Open Policy Agent Engine.

#### Open Policy Agent Engine
The OPA engine evaluates policy against resources using an 
[Open Policy Agent](https://www.openpolicyagent.org/) server. Policies need to 
be namespaced properly for the OPA Engine to locate them and evaluate policy 
properly. 

**Note:** This will not work in cases where policy enforcement is more complicated 
than minor edits to the body of the resource. All remediation is implemented 
in OPA's policy language Rego.

Each unique GCP API should have its own directory with Rego constraints under 
the `policy` directory. For example, to create constraints for the 
`GKE Cluster Nodepool` resource type, look for the container directory, 
as `container.googleapis.com` is the GCP API for this resource type, 
and if it does not exist, create the directory.

For each resource type and desired policy, create a Rego constraint file that 
implements the following rules:

- `valid`: Returns true if the provided input resource adheres to the policy.
- `remediate`: Returns the input resource altered to adhere to policy.
 
The policies should be namespaced as `gcp.<resource.type()>.policy.<policy_name>`. 
For example, the `rpe.resources.gcp.GcpGkeClusterNodepool` resource has a 
type of `container.projects.locations.clusters.nodePools`, so a policy requiring 
auto repairs and auto updates to be enabled might be namespaced 
`gcp.container.projects.locations.clusters.nodePools.policy.auto_repair_upgrade_enabled`.

Below is an example `gke_nodepool_auto_repair_update_enabled.rego` file that 
defines a policy requiring auto repairs and auto updates to be enabled for 
`GKE Cluster Nodepools` by evaluating the resource with the given policy and 
the steps to remediate the resource:

```
package gcp.container.projects.locations.clusters.nodePools.policy.auto_repair_upgrade_enabled

#####
# Resource metadata
#####

labels = input.labels

#####
# Policy evaluation
#####

default valid = false

# Check if node autorepair is enabled
valid = true {
  input.management.autoRepair == true
  input.management.autoUpgrade == true
}

# Check for a global **exclusion based on resource labels
valid = true {
  data.exclusions.label_exclude(labels)
}

#####
# Remediation
#####

remediate = {
  "_remediation_spec": "v2beta1",
  "steps": [
    enable_node_auto_repair_upgrade
  ]
}

enable_node_auto_repair_upgrade = {
    "method": "setManagement",
    "params": {
        "name": combinedName,
        "body":  {
            "name": combinedName,
            "management": {
              "autoRepair": true,
              "autoUpgrade": true
            }
        }
    }
}

# break out the selfLink so we can extract the project, region, cluster and name
selfLinkParts = split(input.selfLink, "/")
# create combined resource name
combinedName = sprintf("projects/%s/locations/%s/clusters/%s/nodePools/%s", [selfLinkParts[5], selfLinkParts[7], selfLinkParts[9], selfLinkParts[11]])
 ```

For each resource type, create a Rego constraint file with a policies rule and 
a violations rule. This allows the OPA engine to query all violations for a 
given resource type in a single API call. 

Below is an example `common.rego` file for the `GKE Cluster Nodepool` resource type:
`package gcp.container.projects.locations.clusters.nodePools`:

```
policies [policy_name] {
    policy := data.gcp.container.projects.locations.clusters.nodePools.policy[policy_name]
}

violations [policy_name] {
    policy := data.gcp.container.projects.locations.clusters.nodePools.policy[policy_name]
    policy.valid != true
}
```

## Examples

#### Using the OPA engine

This assumes you have the `opa` binary in your path

```
# First, start opa with our policies
opa run --server ./policy/
```

Now we need to create an RPE instance with the opa engine configured to use the local OPA server:

```
from rpe import RPE

config = {
    'policy_engines': [
        {
            'type': 'opa',
            'url': 'http://localhost:8181/v1/data'
        }
    ]
}

# Create a resource object with details about the resource we want to evaluate
res = Resource.factory(
  'gcp',
  {
    'resource_name':'my-sql-instance-name',
    'project_id':'my-gcp-project',
    'resource_type':'sqladmin.instances'
  },
  credentials=<gcp-credentials>
)

rpe = RPE(config)
violations = rpe.violations(res)

for (engine, violation) in violations:
    print(engine, violation)
    engine.remediate(res, violation)
```



# Uses

* [Forseti Real-time Enforcer](https://github.com/forseti-security/real-time-enforcer) - The Forseti Real-time enforcer uses rpe-lib for the evaluation and enforcement of policy for Google Cloud resources. It uses a Stackdriver log export to a Pub/Sub topic to trigger enforcement.
