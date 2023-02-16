#!/usr/bin/env python3
import urllib
import base64
import cdsapi
import ast
import inspect
import logging
from typing import List

from annexremote import Master, RemoteError, SpecialRemote




logger = logging.getLogger("datalad.download-cds.cdsrequest")

cdsrequest_REMOTE_UUID = "1da43985-0b6e-4123-89f0-90b88021ed34"


class HandleUrlError(Exception):
    pass

def fromUrl(url: str)->str:
    if not url.startswith("cdsrequest:v1-"):
        raise ValueError("unsupported URL value encountered")
    return (
        base64.urlsafe_b64decode(
            urllib.parse.unquote(
                url.replace("cdsrequest:v1-","")
            ).encode("utf-8")
        ).decode("utf-8")
    )

class CdsRemote(SpecialRemote):

    transfer_store = None
    remove = None

    def initremote(self) -> None:
        pass

    def prepare(self) -> None:
        pass

    def _execute_cds(self, request: str,filename) -> None:
        dictStart=request.index("{")
        dataset_to = request[0:dictStart]
        request_dict_str = request[dictStart:len(request)]
        logger.debug("downloading %s", dataset_to)

        request_dict = ast.literal_eval(request_dict_str)
        c = cdsapi.Client()
        c.retrieve(dataset_to,request_dict,filename)

    def transfer_retrieve(self, key: str,filename) -> None:
        logger.debug(
            "%s called with key %s and filename %s",
            inspect.stack()[0][3],
            key,
        )
        urls = self.annex.geturls(key, "cdsrequest:")
        logger.debug("urls for this key: %s", urls)
        for url in urls:
            self._execute_cds(fromUrl(url),filename)

    def checkpresent(self, key: str) -> bool:
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