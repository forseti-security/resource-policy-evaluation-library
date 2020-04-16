from abc import ABC, abstractmethod

# Base class for policy engines
class Engine(ABC):

    @abstractmethod
    def policies(self):
        pass

    @abstractmethod
    def evaluate(self, resource):
        pass

    @abstractmethod
    def remediate(self, resource, policy_id):
        pass
