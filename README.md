# micromanager

The micro-manager evaluates whether or not a given resource adheres to defined policies. It also attempts to remediate any policy violations.

[![Build Status](https://travis-ci.com/cleardataeng/micromanager.svg?branch=master)](https://travis-ci.com/cleardataeng/micromanager)
[![PyPI version](https://badge.fury.io/py/micromanager.svg)](https://badge.fury.io/py/micromanager)


---

## Resources

The `resource` classes define how to retrieve objects from the google apis. Minimal config is needed to add a new resource from a google api. A `resource` needs to implement a `get`, an `update`, and a `type` method. The `type` method may be used to determine which policies apply to a specific resource.


## Engines

The policy evaluation and enforcement is handled by _policy engines_. Currently there are 2 engines, one based on [Open Policy Agent] (https://www.openpolicyagent.org/), and one that supports arbitrary python for evaluation/enforcement.

### Open Policy Agent Engine

The OPA engine requires that you run the OPA server with policies imported in a specific schema. The policies should be namespaced as `<resource.type()>.policy.<policy_name>`. For example, the GCP SQL Instance resource has a type of `gcp.sqladmin.instances`, so a policy requiring backups to be enabled might be namespaced `gcp.sqladmin.instances.policy.backups`. The policy should implement the following rules:

* `valid`: <boolean>. Returns true if the provided resource adheres to the policy
* `remediate`: <object>. Returns the `input` resource altered to adhere to policy

Each resource type must also implement `policies` and `violations` rule. These probably wont need to change, other than the package name, and look like this:

```
package gcp.sqladmin.instances

policies [policy_name] {
    policy := data.gcp.sqladmin.instances.policy[policy_name]
}

violations [policy_name] {
    policy := data.gcp.sqladmin.instances.policy[policy_name]
    policy.valid != true
}
```

#### Using the OPA engine

This assumes you have the `opa` binary in your path

```
# First, start opa with our policies
opa run --server ./policy/
```

Now we need to create a MicroManager instance with the opa engine configured to use the local OPA server:

```
from micromanager import MicroManager

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
  {
    'resource_name':'my-sql-instance-name',
    'project_id':'my-gcp-project',
    'resource_kind':'sql#instance' # Note: This will likely change to a resource type because the `kind` isn't available in all cases
  },
  credentials=<gcp-credentials>
)

mm = MicroManager(config)
violations = mm.violations(res)

for (engine, violation) in violations:
    print(engine, violation)
    engine.remediate(res, violation)
```
