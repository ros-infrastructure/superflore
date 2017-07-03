from __future__ import print_function

try:
    import pkg_resources
    try:
        __version__ = pkg_resources.require('ebuild_generator')[0].version
    except pkg_resources.DistributionNotFound:
        __version__ = 'unset'
except (ImportError, OSError):
    __version__ = 'unset'

from .repo_instance import repo_instance
from .repo_instance import CloneException
from .repo_instance import BranchException

__all__ = [
    'repo_instance',
    'CloneException',
    'BranchException'
]
