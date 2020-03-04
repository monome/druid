from setuptools import setup, find_packages

# Read the contents of the readme to publish it to PyPI
with open("README.md") as readme:
    long_description = readme.read()

setup(
    name="monome-druid",
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
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    use_scm_version=True,
    python_requires=">=3.6",
    setup_requires=[
        "setuptools_scm",
        "setuptools_scm_git_archive",
    ],
    install_requires=[
        "Click>=7.0",
        "prompt-toolkit>=2.0.10,<3.0",
        "pyserial>=3.4",
        "setuptools",
        "setuptools_scm",
        "setuptools_scm_git_archive",
    ],
    extras_require={
        "test": [
            "pylint",
        ]
    },
    entry_points={
        "console_scripts": [
            "druid=druid.cli:cli",
        ],
    },
)
