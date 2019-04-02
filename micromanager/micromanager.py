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


from .engines import OpenPolicyAgent
from .engines import PythonPolicyEngine


class MicroManager:

    def __init__(self, config):
        self.policy_engines = []

        for pe_config in config['policy_engines']:
            self._add_policy_engine(pe_config)

    def _add_policy_engine(self, pe_config):
        if pe_config.get('type') == 'opa':
            engine = OpenPolicyAgent(pe_config['url'])
        elif pe_config.get('type') == 'python':
            engine = PythonPolicyEngine(pe_config['path'])
        else:
            raise AttributeError("Unrecognized policy engine configuration")

        self.policy_engines.append(engine)

    def get_configured_policies(self):
        policies = {}
        for pe in self.policy_engines:
            policies[str(pe)] = pe.configured_policies()

        return policies

    def violations(self, resource):
        violations = []
        for pe in self.policy_engines:
            for v in pe.violations(resource):
                violations.append((pe, v))

        return violations
