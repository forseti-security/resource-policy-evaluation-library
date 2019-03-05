from urllib import request
from urllib.error import URLError
import json


class NoSuchEndpoint(URLError):
    pass


class OpenPolicyAgent:

    def __init__(self, opa_base_url):
        self.opa_base_url = opa_base_url

    def configured_policies(self):
        return self._opa_request('policies/list')

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

        resource.update(remediated)
