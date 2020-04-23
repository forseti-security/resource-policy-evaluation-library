# resource-policy-evaluation-library

rpe-lib is made up of `Policy Engines (rpe.engines.Engine)` and `Resources (rpe.resources.Resource)`.

`Resources` produce details about the current state of a given type of resource. A resource can be just about anything, but the initial goal of the project was to support Google Cloud Platform (GCP) resources. The implemention is intentionally generic to allow support for other resource types

`Policy Engines` evaluate `Resources` against their configured policies. Given a resource, they can return a list of `Evaluations (rpe.policy.Evaluation)` indicating the name of each policy that applies to the resource (by resource type), and whether or not the resource is compliant. `Resource` also define a `remediate()` function, that should be able to take a dictionary description of how to manipulate a resource to make it compliant.

As an example, for GCP resources, the `remediate()` function expects details about what method to call in the Google REST API for the given resource, and what parameters to pass. So for a Google Cloud Storage Bucket, a policy that enforces bucket versioning could define remediation as a call to the buckets `patch()` method with the appropriate arguments to enable versioning.

[![Build Status](https://api.travis-ci.org/forseti-security/resource-policy-evaluation-library.svg?branch=master)](https://travis-ci.org/forseti-security/resource-policy-evaluation-library/)
[![PyPI version](https://badge.fury.io/py/rpe-lib.svg)](https://badge.fury.io/py/rpe-lib)

---

## Policy Engines

There are currently 2 `Policy Engines` included with rpe-lib:

### Open Policy Agent (opa) Engine

The Open Policy Agent engine uses the Open Policy Agent REST API to evalute policy for a given resource. In order to use this engine, you'll need to run the opa server with the rpe-lib base policies, and whatever policies you'd like to evaluate and optionally enforce. The opa engine passes the result of `Resource.get()` to the opa server as input. All policies need to be defined in the `rpe.policy` namespace, include a few specific rules, and operate on the `input` document:

* _applies\_to_: a list of resource types the policy applies to
* _description_: a human-readable description of the policy
* _compliant_: returns true if the resource defined in the `input` document adheres to the policy
* _excluded_: returns true if there is a reason to exclude the resource from evaluation, for GCP we define resource labels that can mark a resource as excluded
* _remediate (optional)_: returns a JSON object explaining how to remediate the resource for the given policy

Example policy:

```
# This is a real policy included with rpe-lib though slightly simplified
package rpe.policy.storage_buckets_require_object_versioning

description = "Require object versioning for storage buckets"

applies_to = ["storage.googleapis.com/Bucket"]

default compliant = false

default excluded = false

compliant {
        input.resource.versioning.enabled = true
}

excluded {
        input.resource.labels["forseti-enforcer"] = "disabled"
}

remediate = {
        "_remediation_spec": "v2",
        "steps": [
            "method": "patch",
            "params": {
                    "bucket": input.resource.name,
                    "body": {"versioning": {"enabled": true}},
            }
        ]
}
```

### Python Engine
The OPA engine is very powerful, but is limited by what OPA is capable of. For use-cases that are more complicated, you might want to use the python engine. This engine expects the path to a python package that contains classes that perform the evaluation, and optionally remediation.

As mentioned, the python policies are actually classes. Here is an example python policy class:

```
# Stubbed out example of the above OPA engine policy as a python engine policy
class GCPBucketVersioningPolicy:
    description = 'Require object versioning for storage buckets'
    applies_to = ['cloudresourcemanager.googleapis.com/Project']

    @classmethod
    def compliant(cls, resource):
        return resource.get()['resource']['versioning']['enabled'] == True

    @classmethod
    def excluded(cls, resource):
        return resource.get()['resource']['labels']['forseti-enforcer'] == 'disabled'

    @classmethod
    def remediate(cls, resource):
        # execute cloudfuntion to enable versioning,
        # or shell execute gsutil,
        # or anything you can do with python
        pass
```

## Resources

`Resources` must define the following functions

* `get()`: returns metadata describing the current state of the resource
* `remediate(remediation_spec)`: applies the remediation (the spec is specific to the resource type/implementation)
* `type()`: returns the type of resource, used by policy engines to determine which policies apply to a given resource

## Examples

#### Using the OPA engine

This assumes you have the `opa` binary in your path

```
# First, start opa with our policies
opa run --server ./policy/
```

Now we need to create an RPE instance with the opa engine configured to use the local OPA server:

```python
from rpe import RPE
from rpe.resources import GoogleAPIResource

config = {
    'policy_engines': [
        {
            'type': 'opa',
            'url': 'http://localhost:8181/v1/data'
        }
    ]
}

rpe = RPE(config)

# Create a resource object for the resource we want to evaluate
res = GoogleAPIResource.from_cai_data(
    '//storage.googleapis.com/my-test-bucket',
    'storage.googleapis.com/Bucket',
    project_id='my-test-project',
)

evals = rpe.evaluate(res)

for e in evals:
    print(f'Policy: {e.policy_id}, Compliant: {e.compliant}')

    if not e.compliant and e.remediable:
        e.remediate()
```



# Applications using rpe-lib

* [Forseti Real-time Enforcer](https://github.com/forseti-security/real-time-enforcer) - The Forseti Real-time enforcer uses rpe-lib for the evaluation and enforcement of policy for Google Cloud resources. It uses a Stackdriver log export to a Pub/Sub topic to trigger enforcement.
