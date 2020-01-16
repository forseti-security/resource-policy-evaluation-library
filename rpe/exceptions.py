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


from googleapiclient.errors import HttpError
from urllib.error import URLError


def is_retryable_exception(err):
    """
    Args:
        err: An exception

    Returns:
        True if the exception should trigger a retry of certain operations

    """
    if isinstance(err, HttpError):
        if err.resp.status == 400 and 'resourceNotReady' in err.content.decode('utf-8'):
            return True
        else:
            return err.resp.status in [409]

    if isinstance(err, URLError):
        return not isinstance(err, NoSuchEndpoint)

    return False


class NoSuchEndpoint(URLError):
    pass


class NoPossibleRemediation(Exception):
    pass


class ResourceException(Exception):
    pass

class UnsupportedRemediationSpec(Exception):
    pass


class InvalidRemediationSpecStep(Exception):
    pass
