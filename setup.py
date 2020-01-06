import sys
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))


# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gce",
    version="1.0.2",
    description="Script Python pour interroger un module Teleinfo de GCE Electronics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rene-d/gce",
    author="Rene Devichi",
    author_email="rene.github@gmail.com",
    classifiers=[
        "License :: Public Domain",
        "Operating System :: OS Independent",
        "Topic :: Home Automation",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="teleinfo teleinformation gce",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.5, <4",
    install_requires=["requests"],
    entry_points={"console_scripts": ["gce=gce.gce:main"]},
    project_urls={
        "Source": "https://github.com/rene-d/gce",
        "Bug Reports": "https://github.com/rene-d/gce/issues",
    },
)
