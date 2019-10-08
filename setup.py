#!/usr/bin/env python3
from setuptools import setup, find_namespace_packages

# Read the contents of the readme to publish it to PyPI
with open("README.md") as readme:
    long_description = readme.read()

setup(
    name="monome-druid",
    version="0.1.1",
    description="Terminal interface for crow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/monome/druid",
    author="monome",
    author_email="bcrabtree@monome.org",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=find_namespace_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=[
        "prompt-toolkit>=2.0.10",
        "pyserial>=3.4",
    ],
    extras_require={
        "test": [
            "pylint",
        ]
    },
    entry_points={
        "console_scripts": [
            "druid=druid.main:main",
        ],
    },
)
