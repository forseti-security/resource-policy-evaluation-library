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


import importlib.util
import inspect


class PythonPolicyEngine:
    def __init__(self, package_path):
        self.package_path = package_path
        self._load_module()
        self._build_policy_map()

    def _load_module(self):
        """Todo: Make this to work on different python versions"""
        spec = importlib.util.spec_from_file_location(
            "pypol",
            "{}/__init__.py".format(self.package_path)
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.module = module

    def _build_policy_map(self):
        """Loop through all classes that are part of this module and build a map
        of policies by resource type
        """
        self.policy_map = {}
        for name, obj in inspect.getmembers(self.module):
            if inspect.isclass(obj):
                if hasattr(obj, 'applies_to'):
                    if isinstance(obj.applies_to, list):
                        for resource_type in obj.applies_to:
                            if resource_type not in self.policy_map:
                                self.policy_map[resource_type] = []
                            self.policy_map[resource_type].append(obj)

    def configured_policies(self):
        # adding for compatibility
        # todo: implement me
        return []

    def policies(self, resource):
        """
        Args:
            resource: The resource we'd like to evaluate

        Returns:
            A list of names of policies that apply to the provided resource

        """
        return self.policy_map[resource.type()]

    def violations(self, resource):
        """
        Args:
            resource: The resource we'd like to evaluate

        Returns:
            A list of names of policies this resource violates

        """
        violations = []
        for cls in self.policies(resource):
            policy = cls(resource)
            if not policy.evaluate():
                violations.append(policy)
        return violations

    def remediate(self, resource, violation):
        violation.remediate(resource)
