"""DataLad demo extension"""

__docformat__ = 'restructuredtext'

import logging
lgr = logging.getLogger('datalad.cds')

# Defines a datalad command suite.
# This variable must be bound as a setuptools entrypoint
# to be found by datalad
command_suite = (
    # description of the command suite, displayed in cmdline help
    "TestNachricht",
    [
        # specification of a command, any number of commands can be defined
        (
            # importable module that contains the command implementation
            'datalad_cds_extension.cds',
            # name of the command class implementation in above module
            'CDS',
            # optional name of the command in the cmdline API
            'CDS-loader',
            # optional name of the command in the Python API
            'datalad_cds'
        ),
    ]
)

from . import _version
__version__ = _version.get_versions()['version']
