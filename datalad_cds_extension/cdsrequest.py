#!/usr/bin/env python3
import cdsapi
import ast
import inspect
import logging
from typing import List

from annexremote import Master, RemoteError, SpecialRemote

from datalad_cds_extension.spec import Spec


logger = logging.getLogger("datalad.download-cds.cdsrequest")

cdsrequest_REMOTE_UUID = "1da43985-0b6e-4123-89f0-90b88021ed34"


class HandleUrlError(Exception):
    pass


class CdsRemote(SpecialRemote):

    transfer_store = None
    remove = None

    def initremote(self) -> None:
        # setting the uuid here unfortunately does not work, initremote is
        # executed to late
        # self.annex.setconfig("uuid", cdsrequest_REMOTE_UUID)
        pass

    def prepare(self) -> None:
        pass

    def _execute_cds(self, list: List[str],filename) -> None:
        user_input = list[0]
        logger.debug("downloading %s", user_input)
        #self.annex.info("executing {}".format(user_input))

        request_dict = ast.literal_eval(list[1])
        c = cdsapi.Client()
        c.retrieve(list[0],request_dict,filename)

    def _handle_url(self, url: str,filename) -> None:
        import datalad.api as da
        from datalad.utils import swallow_outputs

        spec = Spec.from_url(url)
        inputs = spec.inputs
        if inputs:
            with swallow_outputs() as cm:
                logger.info("fetching inputs: %s", inputs)
                da.get(set(inputs))
                logger.info("datalad get output: %s", cm.out)
        cmd = spec.cmd
        self._execute_cds(cmd,filename)

    def transfer_retrieve(self, key: str,filename) -> None:
        logger.debug(
            "%s called with key %s and filename %s",
            inspect.stack()[0][3],
            key,
        )
        urls = self.annex.geturls(key, "cdsrequest:")
        logger.debug("urls for this key: %s", urls)
        for url in urls:
            try:
                self._handle_url(url,filename)
                break
            except HandleUrlError:
                pass
        else:
            raise RemoteError("Failed to handle key {}".format(key))

    def checkpresent(self, key: str) -> bool:
        # We just assume that we can always handle the key
        return True

    def claimurl(self, url: str) -> bool:
        return url.startswith("cdsrequest:")

    def checkurl(self, url: str) -> bool:
        return url.startswith("cdsrequest:")
        

def main():
    master = Master()
    remote = CdsRemote(master)
    master.LinkRemote(remote)
    logger.addHandler(master.LoggingHandler())
    master.Listen()

if __name__ == "__main__":
    main()