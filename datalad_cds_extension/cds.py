"""DataLad demo command"""

__docformat__ = 'restructuredtext'

from os.path import curdir
from os.path import abspath

from datalad.interface.base import Interface
from datalad.interface.base import build_doc
from datalad.support.param import Parameter
from datalad.distribution.dataset import datasetmethod
from datalad.interface.utils import eval_results
from datalad.support.constraints import EnsureChoice

from datalad.interface.results import get_status_dict

import cdsapi

import logging
lgr = logging.getLogger('datalad.cds.datalad_cds')


# decoration auto-generates standard help
@build_doc
# all commands must be derived from Interface
class CDS(Interface):
    # first docstring line is used a short description in the cmdline help
    # the rest is put in the verbose help and manpage
    """Short description of the command

    Long description of arbitrary volume.
    """

    # parameters of the command, must be exhaustive
    _params_ = dict(

        json=Parameter(
            args=("-json"),
            doc="""json file with cds-api line"""
        ),




        # name of the parameter, must match argument name
        language=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-l", "--language"),
            # documentation
            doc="""language to say "hello" in""",
            # type checkers, constraint definition is automatically
            # added to the docstring
            constraints=EnsureChoice('en', 'de')),
    )

    @staticmethod
    # decorator binds the command to the Dataset class as a method
    @datasetmethod(name='datalad_cds')
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(json):
        f=open(json)
        c=cdsapi.Client()
        c.retrieve(f.read())         
    
    
    def __call__(language='en'):
        if language == 'en':
            msg = 'Hello!'
        elif language == 'de':
            msg = 'Tachchen!'
        else:
            msg = ("unknown language: '%s'", language)

        # commands should be implemented as generators and should
        # report any results by yielding status dictionaries
        yield get_status_dict(
            # an action label must be defined, the command name make a good
            # default
            action='demo',
            # most results will be about something associated with a dataset
            # (component), reported paths MUST be absolute
            path=abspath(curdir),
            # status labels are used to identify how a result will be reported
            # and can be used for filtering
            status='ok' if language in ('en', 'de') else 'error',
            # arbitrary result message, can be a str or tuple. in the latter
            # case string expansion with arguments is delayed until the
            # message actually needs to be rendered (analog to exception
            # messages)
            message=msg)
