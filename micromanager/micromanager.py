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

    def violations(self, resource):
        violations = []
        for pe in self.policy_engines:
            for v in pe.violations(resource):
                violations.append((pe, v))

        return violations
