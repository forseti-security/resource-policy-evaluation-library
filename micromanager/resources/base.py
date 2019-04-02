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


from abc import ABC, abstractmethod


class Resource(ABC):

    @staticmethod
    def factory(platform, resource_data, **kargs):
        """ Return a resource from the appropriate platform """
        from .gcp import GoogleAPIResource

        resource_platform_map = {
            'gcp': GoogleAPIResource
        }

        try:
            resource = resource_platform_map[platform].factory(
                resource_data,
                **kargs
            )
        except KeyError:
            raise AttributeError('Unrecognized platform')

        return resource

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def type(self):
        pass
