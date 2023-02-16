"""DataLad demo extension"""

__docformat__ = 'restructuredtext'

import logging

from . import _version
lgr = logging.getLogger('datalad.downloadcds')

__version__=_version.get_versions()["version"]

# Defines a datalad command suite.
# This variable must be bound as a setuptools entrypoint
# to be found by datalad
command_suite = (
    # description of the command suite, displayed in cmdline help
    "DataLad download-cds command suite",
    [
        # specification of a command, any number of commands can be defined
        (
            # importable module that contains the command implementation
            'datalad_cds_extension.downloadcds',
            # name of the command class implementation in above module
            'DownloadCDS',
            # optional name of the command in the cmdline API
            'download-cds',
            # optional name of the command in the Python API
            'download_cds'
        ),
    ]
)

from . import _version
__version__ = _version.get_versions()['version']
