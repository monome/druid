import pkg_resources

from setuptools_scm import get_version

try:
    __version__ = get_version()
except LookupError:
    from pkg_resources import get_distribution
    __version__ = get_distribution("monome-druid").version
