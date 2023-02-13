"""DataLad demo command"""

__docformat__ = 'restructuredtext'
import os.path as op
import json
from typing import Dict, Iterable, List, Literal, Optional
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
from datalad_cds_extension.spec import Spec
import logging
logger = logging.getLogger('datalad.cds.datalad_cds')


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
        readfile = open(user_string_input)
        readstr = readfile.read()
        cmd = [readstr]
        ds = None
        try:
            ds = require_dataset(
                dataset, check_installed=True,
                purpose='download cds')
        except NoDatasetFound:
            pass
        path = str(resolve_path(path or op.curdir, ds=dataset))
        spec = Spec(cmd,None)
        logger.debug("spec is %s", spec)
        url = spec.to_url()
        logger.debug("url is %s", url)
        pathobj = ds.pathobj / path
        logger.debug("target path is %s", pathobj)
        ensure_special_remote_exists_and_is_enabled(ds.repo, "cdsrequest")
        ds.repo.add_url_to_file(pathobj, url)
        msg = """\
[DATALAD cdsrequest] {}
=== Do not change lines below ===
{}
^^^ Do not change lines above ^^^
        """
        cmd_message_full = "'" + "' '".join(spec.cmd) + "'"
        cmd_message = (
            cmd_message_full
            if len(cmd_message_full) <= 40
            else cmd_message_full[:40] + " ..."
        )
        record = json.dumps(spec.to_dict(), indent=1, sort_keys=True)
        msg = msg.format(cmd_message,
            record,
        )
        yield ds.save(pathobj, message=msg)
        yield get_status_dict(action="cdsrequest", status="ok")

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