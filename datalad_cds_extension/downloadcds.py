"""DataLad cds downloader"""

__docformat__ = 'restructuredtext'
import base64
import urllib.parse
import os.path as op
from typing import Dict, Iterable, List, Literal
from datalad.interface.base import Interface
from datalad.interface.base import build_doc
from datalad.support.param import Parameter
from datalad.support.annexrepo import AnnexRepo
from datalad.distribution.dataset import datasetmethod
from datalad.interface.utils import eval_results
from datalad.distribution.dataset import (
    EnsureDataset,
    datasetmethod,
    require_dataset,
    resolve_path
)
from datalad.support.constraints import (
    EnsureNone,
    EnsureStr,
)
from datalad.interface.common_opts import (
    nosave_opt,
    save_message_opt,
)
from datalad.support.exceptions import (
    NoDatasetFound,
)

from datalad.interface.results import get_status_dict
import datalad_cds_extension.cdsrequest
import logging
logger = logging.getLogger('datalad.cds.download-cds')


# decoration auto-generates standard help
@build_doc
# all commands must be derived from Interface
class DownloadCDS(Interface):
    # first docstring line is used a short description in the cmdline help
    # the rest is put in the verbose help and manpage
    """Short description of the command

    Long description of arbitrary volume.
    """

    # parameters of the command, must be exhaustive
    _params_ = dict(

        user_string_input=Parameter(
            doc="""json file with retrieve request"""),
        dataset=Parameter(
            args=("-d", "--dataset"),
            metavar='PATH',
            doc="""specify the dataset to add files to. If no dataset is given,
            an attempt is made to identify the dataset based on the current
            working directory. Use [CMD: --nosave CMD][PY: save=False PY] to
            prevent adding files to the dataset.""",
            constraints=EnsureDataset() | EnsureNone()),

        overwrite=Parameter(
            args=("-o", "--overwrite"),
            action="store_true",
            doc="""flag to overwrite it if target file exists"""),

        path=Parameter(
            args=("-O", "--path"),
            doc="""target for download. If the path has a trailing separator,
            it is treated as a directory, and each specified URL is downloaded
            under that directory to a base name taken from the URL. Without a
            trailing separator, the value specifies the name of the downloaded
            file (file name extensions inferred from the URL may be added to it,
            if they are not yet present) and only a single URL should be given.
            In both cases, leading directories will be created if needed. This
            argument defaults to the current directory.""",
            constraints=EnsureStr() | EnsureNone()),

        archive=Parameter(
            args=("--archive",),
            action="store_true",
            doc="""pass the downloaded files to [CMD: :command:`datalad
            add-archive-content --delete` CMD][PY: add_archive_content(...,
            delete=True) PY]"""),

        save=nosave_opt,

        message=save_message_opt
    )

    @staticmethod
    # decorator binds the command to the Dataset class as a method
    @datasetmethod(name='download_cds')
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        user_string_input,
        dataset=None, path=None, overwrite=False,
        archive=False, save=True, message=None
    ) -> Iterable[Dict]:
        
        inputList = fileToList(user_string_input)
        request_str = inputList[0]
        ds = None
        if(not path):
            path = inputList[1]
            """
            if(not op.exists(path)):
                raise ValueError("The path in the file is not valid!")
            """

        try:
            ds = require_dataset(
                dataset, check_installed=True,
                purpose='download cds')
        except NoDatasetFound:
            pass

        path = str(resolve_path(path or op.curdir, ds=dataset))
        url = toUrl(request_str)
        logger.debug("url is %s", url)
        pathobj = ds.pathobj / path
        logger.debug("target path is %s", pathobj)

        ensure_special_remote_exists_and_is_enabled(ds.repo, "cdsrequest")
        ds.repo.add_url_to_file(pathobj, url)

        msg = """\
[DATALAD cdsrequest] {}
=== Do not change lines below ===
This was the request:
{}
^^^ Do not change lines above ^^^
        """

        msg = msg.format(message if message is not None else "",
            request_str,
        )
        
        yield ds.save(pathobj, message=msg)
        yield get_status_dict(action="cdsrequest", status="ok")
        if(archive):
            yield from ds.add_archive_content(
                                pathobj,
                                delete=True,
                                on_failure='ignore',
                                return_type='generator',
                                result_renderer='disabled'
                            )

def ensure_special_remote_exists_and_is_enabled(
    repo: AnnexRepo, remote: Literal["cdsrequest"]
) -> None:
    
    """Initialize and enable the cdsrequest special remote, if it isn't already.
    Very similar to datalad.customremotes.base.ensure_datalad_remote.
    """

    uuids = {"cdsrequest": datalad_cds_extension.cdsrequest.cdsrequest_REMOTE_UUID}
    uuid = uuids[remote]

    name = repo.get_special_remotes().get(uuid, {}).get("name")
    if not name:
        repo.init_remote(
            remote,
            [
                "encryption=none",
                "type=external",
                "autoenable=true",
                "externaltype={}".format(remote),
                "uuid={}".format(uuid),
            ],
        )

    elif repo.is_special_annex_remote(name, check_if_known=False):
        logger.debug("special remote %s is enabled", name)

    else:
        logger.debug("special remote %s found, enabling", name)
        repo.enable_remote(name)

def fileToList(input_file) -> List[str]:
    readfile = open(input_file)
    readstr = readfile.read()

    startDict = readstr.index('{')
    endDict = readstr.index('}')
    string_server = readstr[0:startDict]
    dictString = readstr[startDict:endDict+1]
    string_to = readstr[endDict+1:len(readstr)]

    dictString.replace("\n","")
    string_server = string_server[1:len(string_server)-1]
    string_to = string_to[1:len(string_to)-1]

    string_server=string_server.replace("\n","")
    string_server=string_server.replace(",","")
    string_server=string_server.replace("\"","")
    string_server=string_server.replace("'","")
    string_server=string_server.replace(" ","")

    string_to=string_to.replace(",","")
    string_to=string_to.replace("\"","")
    string_to=string_to.replace("'","")
    string_to=string_to.replace("\n","")
    string_to=string_to.replace(" ","")

    return [string_server+dictString,string_to]

def toUrl(request: str):

    return "cdsrequest:v1-" + urllib.parse.quote(base64.urlsafe_b64encode(request.encode("utf-8")))
