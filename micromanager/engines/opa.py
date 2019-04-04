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


import json
import tenacity

from urllib import request

from micromanager.exceptions import is_retryable_exception
from micromanager.exceptions import NoSuchEndpoint
from micromanager.exceptions import NoPossibleRemediation


class OpenPolicyAgent:

    def __init__(self, opa_base_url):
        self.opa_base_url = opa_base_url

    def configured_policies(self):
        return self._opa_request('policies/list')

    @tenacity.retry(
        retry=tenacity.retry_if_exception(is_retryable_exception),
        wait=tenacity.wait_random_exponential(multiplier=1, max=10),
        stop=tenacity.stop_after_attempt(5)
    )
    def _opa_request(self, path, method='GET', data=None):
        url = '{}/{}'.format(self.opa_base_url, path)
        headers = {'Content-type': 'application/json'}
        req = request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            method=method,
            headers=headers
        )

        with request.urlopen(req) as resp:
            decoded_resp = resp.read().decode('utf-8')
            deserialized_resp = json.loads(decoded_resp)
            if 'result' not in deserialized_resp:
                err = "Endpoint {} not found on the OPA server.".format(url)
                raise NoSuchEndpoint(err)

            return deserialized_resp['result']

    def _get_policy_path(self, resource):
        # policy lookups are based on the resource type
        return resource.type().replace('.', '/')

    def policies(self, resource):
        """
        Args:
            resource: The resource we'd like to evaluate

        Returns:
            A list of names of policies that apply to the provided resource

        """
        policies_path = '{}/policies'.format(
            self._get_policy_path(resource)
        )
        return self._opa_request(policies_path)

    def violations(self, resource):
        """
        Args:
            resource: The resource we'd like to evaluate

        Returns:
            A list of names of policies this resource violates

        """
        violations_path = '{}/violations'.format(
            self._get_policy_path(resource)
        )
        input = {'input': resource.get()}
        return self._opa_request(violations_path, method='POST', data=input)

    def remediate(self, resource, violation):
        rem_path = '{}/policy/{}/remediate'.format(
            self._get_policy_path(resource),
            violation
        )
        input = {'input': resource.get()}
        remediated = self._opa_request(rem_path, method='POST', data=input)

        if remediated:
            resource.update(remediated)
        else:
            raise NoPossibleRemediation("Remediation is not possible")
