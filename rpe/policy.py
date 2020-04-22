from dataclasses import dataclass
from typing import List

from rpe.engines import Engine
from rpe.resources import Resource

@dataclass
class Policy:
    policy_id: str
    engine: Engine
    applies_to: List[str]
    description: str = ""

@dataclass
class Evaluation:
    resource: Resource
    engine: Engine
    policy_id: str
    
    compliant: bool
    excluded: bool
    remediable: bool

    def remediate(self):
        return self.engine.remediate(self.resource, self.policy_id)
