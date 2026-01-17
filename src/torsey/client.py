import os
import urllib.parse
from urllib.error import URLError
from urllib.request import urlopen

from torsey.bencoding import decode
from torsey.metadata_info import MetadataInfo

DEFAULT_PORT = 6881


def generatePeerID() -> bytes:
    return b"-TS0001-" + os.urandom(12)


def constructTrackerURL(metadataInfo: MetadataInfo, port: int = DEFAULT_PORT):
    announce = metadataInfo.getAnnounce()
    assert announce is not None
    params = {
        "info_hash": metadataInfo.getInfoHash(),
        "peer_id": generatePeerID(),
        "port": port,
        "uploaded": 0,
        "downloaded": 0,
        "left": metadataInfo.getLength(),
        "compact": 1,
        "event": "started"
    }
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"{announce}?{query}"


def contactTracker(metadataInfo: MetadataInfo, port: int = DEFAULT_PORT):
    data = None
    while data is None:
        try:
            with urlopen(constructTrackerURL(metadataInfo, port)) as response:
                data = response.read()
                break
        except URLError:
            if metadataInfo.announceList is not None:
                metadataInfo.shiftAnnounce()
            else:
                break
    if data is None:
        raise Exception("Could not to contact any of the announces.")
    return decode(data)
