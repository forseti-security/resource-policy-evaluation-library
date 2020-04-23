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


import json
import tenacity

from urllib import request

from rpe.policy import Evaluation, Policy
from rpe.exceptions import is_retryable_exception
from rpe.exceptions import NoSuchEndpoint
from rpe.exceptions import NoPossibleRemediation

from .base import Engine


class OpenPolicyAgent(Engine):

    def __init__(self, opa_base_url):
        self.opa_base_url = opa_base_url

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

    # Perform an evaluation on a given resource
    def evaluate(self, resource):
        input = {
            'input': resource.get(),
        }

        evals = self._opa_request('rpe/evaluate', method='POST', data=input)

        return [
            Evaluation(engine=self, resource=resource, **ev)
            for ev in evals
        ]

    def policies(self):
        """
        Returns:
            A list of all configured policies, optionally filtered by a resource_type
        """
        policies = self._opa_request('rpe/policies')

        return [
            Policy(engine=self, **p)
            for p in policies
        ]

    def remediate(self, resource, policy_id):
        rem_path = 'rpe/policy/{}/remediate'.format(
            policy_id
        )
        input = {'input': resource.get()}
        remediation = self._opa_request(rem_path, method='POST', data=input)

        if remediation:
            resource.remediate(remediation)
        else:
            raise NoPossibleRemediation("Remediation is not supported for this resource/policy")
