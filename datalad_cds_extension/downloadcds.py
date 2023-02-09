"""DataLad demo command"""

__docformat__ = 'restructuredtext'
import os.path as op
import json
from typing import Dict, Iterable, List, Literal, Optional
import datalad.local.download_url 
from datalad.interface.base import Interface
from datalad.interface.base import build_doc
from datalad.support.param import Parameter
from datalad.support.annexrepo import AnnexRepo
from datalad.distribution.dataset import datasetmethod
from datalad.interface.utils import eval_results
from datalad.support.constraints import EnsureChoice
from datalad.distribution.dataset import (
    Dataset,
    EnsureDataset,
    datasetmethod,
    require_dataset,
    resolve_path
)
from datalad.utils import (
    Path,
    PurePosixPath,
    ensure_list_from_str,
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
    CapturedException,      
    CommandError,
    NoDatasetFound,
)

from datalad.interface.results import get_status_dict
#import datalad_cds_extension.downloadcds
import datalad_cds_extension.cdsrequest
import cdsapi
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
        print("Test")
        readfile = open(user_string_input)
        readstr = readfile.read()
        cmd = [readstr]
        ds = None
        if save or dataset:
            try:
                ds = require_dataset(
                    dataset, check_installed=True,
                    purpose='download cds')
            except NoDatasetFound:
                pass

        common_report = {"action": "download_cds", 
                         "ds": ds}

        got_ds_instance = isinstance(dataset, Dataset)
        dir_is_target = not path or str(path).endswith(op.sep)
        path = str(resolve_path(path or op.curdir, ds=dataset))
        if dir_is_target:
            # resolve_path() doesn't preserve trailing separators. Add one for
            # the download() call.
            path = path + op.sep

        if not dir_is_target:
            if archive:
                # make sure the file suffix indicated by a URL is preserved
                # so that any further archive processing doesn't have to
                # employ mime type inspection in order to determine the archive
                # type
                from datalad.support.network import URL
                suffixes = PurePosixPath(URL(user_string_input).path).suffixes
                if not Path(path).suffixes == suffixes:
                    path += ''.join(suffixes)
            # we know that we have a single URL
            # download() would be fine getting an existing directory and
            # downloading the URL underneath it, but let's enforce a trailing
            # slash here for consistency.
            if op.isdir(path):
                yield get_status_dict(
                    status="error",
                    message=(
                        "Non-directory path given (no trailing separator) "
                        "but a directory with that name (after adding archive "
                        "suffix) exists"),
                    type="file",
                    path=path,
                    **common_report)
                return
        print("Zeile 161")
        spec = Spec(cmd,[])
        logger.debug("spec is %s", spec)
        url = spec.to_url()
        logger.debug("url is %s", url)

        pathobj = ds.pathobj / path
        print(pathobj)
        print(url)
        logger.debug("target path is %s", pathobj)

        print("Zeile 170")

        ensure_special_remote_exists_and_is_enabled(ds.repo, "cdsrequest")
        ds.repo.add_url_to_file(pathobj, url)
        print("Zeile 174")
        msg = """\
[DATALAD cdsrequest] {}
=== Do not change lines below ===
{}
^^^ Do not change lines above ^^^
        """
        cmd_message_full = "'" + "' '".join(spec.cmd) + "'"
        print("Zeile 180")

        cmd_message = (
            cmd_message_full
            if len(cmd_message_full) <= 40
            else cmd_message_full[:40] + " ..."
        )
        record = json.dumps(spec.to_dict(), indent=1, sort_keys=True)
        msg = msg.format(cmd_message,
            record,
        )
        print("Zeile 192")
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
    print("ensure remote wurde beendet")