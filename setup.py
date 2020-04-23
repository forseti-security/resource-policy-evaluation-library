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


from __future__ import print_function

from setuptools import setup

setup(
    name="rpe-lib",
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A resource policy evaluation library",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Joe Ceresini",
    url="https://github.com/forseti-security/resource-policy-evaluation-library",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=[
        'google-api-python-client',
        'google-api-python-client-helpers',
        'tenacity',
    ],
    packages=[
        'rpe',
        'rpe.engines',
        'rpe.resources',
    ],
    package_data={},
    license="Apache 2.0",
    keywords="gcp policy enforcement",
)
