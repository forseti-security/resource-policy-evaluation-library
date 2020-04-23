# Copyright 2019 The resource-policy-evaluation-library Authors. All rights reserved.
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


from abc import ABC, abstractmethod


class Resource(ABC):

    # Returns a dictionary representing the resource. Must contain a 'type' key
    # indicating what type of resource it is
    @abstractmethod
    def get(self):
        pass

    # Performs remediation based on a json representation of how to remediate a
    # resource that does not comply to a given policy. This allows for
    # remediation from non-python based engines, such as the open-policy-agent
    # engine
    @abstractmethod
    def remediate(self):
        pass

    # Returns the resource type
    @abstractmethod
    def type(self):
        pass
