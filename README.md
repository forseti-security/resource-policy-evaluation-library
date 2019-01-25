The micro-manager evaluates whether or not a given resource adheres to defined policies. It also attempts to remediate any policy violations.

## Resources

The `resource` classes define how to retrieve objects from the google apis. Minimal config is needed to add a new resource from a google api. A `resource` needs to implement a `get`, and an `update` method.

## Policies

Many policies will be written in Open Policy Agent's Rego language. More to come when the policy format is determined.
