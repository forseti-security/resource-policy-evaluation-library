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


from __future__ import print_function

from setuptools import setup

setup(
    name="micromanager",
    description="Policy enforcement tool for GCP",
    long_description='Tool to load resources from GCP, check them against policies written in Rego, and attempt remediation of policy violations.',
    author="Joe Ceresini",
    url="https://github.com/cleardataeng/micromanager",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=[
        'google-api-python-client',
        'google-api-python-client-helpers',
        'tenacity',
    ],
    packages=[
        'micromanager',
        'micromanager.engines',
        'micromanager.resources',
    ],
    package_data={},
    license="Apache 2.0",
    keywords="gcp policy enforcement",
)

