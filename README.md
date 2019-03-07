# micromanager

The micromanager evaluates whether or not a given resource adheres to defined policies. It also attempts to remediate any policy violations.

[![Build Status](https://travis-ci.com/cleardataeng/micromanager.svg?branch=master)](https://travis-ci.com/cleardataeng/micromanager)
[![PyPI version](https://badge.fury.io/py/micromanager.svg)](https://badge.fury.io/py/micromanager)

---

## Resources

Micromanager expects a fairly simple interface to any resource you wish to evaluate policy on. It expects an object with the following functions defined:

```
class MyResource:

    # Returns the body of a given resource as a dictionary
    def get(self):
        pass

    # Takes the body of a resource, and attempts to update the resource
    def update(self, body):
        pass
    # Returns the resource type as a string
    #  Note: This should be a dotted-string that the engines will use to determine what policies are relevant
    type(self):
        pass
```

Some resources are provided with micromanager, and hopefully that will continue to grow, but it's not required that you use the provided resource classes.

## Engines

The policy evaluation and enforcement is handled by _policy engines_:

### Open Policy Agent Engine

The OPA engine evaluates policy against resources using an [Open Policy Agent](https://www.openpolicyagent.org/) server. Policies need to be namespaced properly for the OPA Engine to locate them, and evaluate policy properly. Note: This won't work in cases where policy enforcement is more complicated that minor edits to the body of the resource. All remediation is implemented in OPA's policy language `Rego`.

The policies should be namespaced as `<resource.type()>.policy.<policy_name>`. For example, the `micromanager.resources.gcp.GcpSqlInstance` resource has a type of `gcp.sqladmin.instances`, so a policy requiring backups to be enabled might be namespaced `gcp.sqladmin.instances.policy.backups`. The policy should implement the following rules:

* `valid`: <boolean>. Returns true if the provided resource adheres to the policy
* `remediate`: <object>. Returns the `input` resource altered to adhere to policy

For each resource.type() you also need to define a `policies` rule and a `violations` rule. This allows the OPA engine to query all violations for a given resource type in a single API call. These probably wont need to change, other than the package name, and look like this (again with the `micromanager.resources.gcp.GcpSqlInstance` example):

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

## Examples

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
  'gcp',
  {
    'resource_name':'my-sql-instance-name',
    'project_id':'my-gcp-project',
    'resource_type':'sqladmin.instances'
  },
  credentials=<gcp-credentials>
)

mm = MicroManager(config)
violations = mm.violations(res)

for (engine, violation) in violations:
    print(engine, violation)
    engine.remediate(res, violation)
```



# Uses

* [Forseti Policy Engine](https://github.com/cleardataeng/forseti-policy-enforcer) - The Forseti Policy Engine uses micromanger for evaluation and enforcment of Google Cloud resources. It uses a Stackdriver log export to a Pub/Sub topic to trigger enforcement
