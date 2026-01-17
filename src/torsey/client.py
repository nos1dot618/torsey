import hashlib
import os
import urllib.parse
from urllib.request import urlopen

from torsey.bencoding import decode, encode
from torsey.metadata_info import MetadataInfo

DEFAULT_PORT = 6881


def generatePeerID() -> bytes:
    return b"-TS0001-" + os.urandom(12)


def constructTrackerURL(metadataInfo: MetadataInfo, port: int = DEFAULT_PORT):
    announce = metadataInfo.getAnnounce()
    assert announce is not None
    params = {
        "info_hash": hashlib.sha1(encode(metadataInfo.info)).digest(),
        "peer_id": generatePeerID(),
        "port": port,
        "uploaded": 0,
        "downloaded": 0,
        "left": metadataInfo.totalLength(),
        "compact": 1,
        "event": "started"
    }
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"{announce}?{query}"


def contactTracker(metadataInfo: MetadataInfo, port: int = DEFAULT_PORT):
    trackerURL = constructTrackerURL(metadataInfo, port)
    with urlopen(trackerURL) as response:
        data = response.read()
    return decode(data)
