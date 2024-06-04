# To upload to PyPi, find the directions here https://packaging.python.org/tutorials/packaging-projects/

import sys
from setuptools import setup

install_requires = ["future", "python-ntlm3", "PyYAML"]

# get our long description from the README.md
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="v1pysdk",
    version="0.8.0",
    description="VersionOne API client",
    # original_author="Joe Koberg (VersionOne, Inc.)",
    author="Samuel Bastiat",
    # original_author_email="Joe.Koberg@versionone.com",
    author_email="s31db.github@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT/BSD",
    keywords="versionone v1 api sdk",
    url="http://github.com/s31db/VersionOne.SDK.Python.git",
    project_urls={
        "Documentation": "http://github.com/s31db/VersionOne.SDK.Python.git",
        "Source": "http://github.com/s31db/VersionOne.SDK.Python.git",
        "Tracker": "http://github.com/s31db/VersionOne.SDK.Python.git/issues",
    },
    packages=[
        "v1pysdk",
    ],
    include_package_data=True,
    install_requires=install_requires,
    classifiers=(
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Bug Tracking",
    ),
    # it may work on others, but this is what has had basic testing
    python_requires=">=3.10, <4",
    tests_require=["testtools", "unittest2"],  # so testtools tests are auto-discovered
    test_suite="tests",
)
