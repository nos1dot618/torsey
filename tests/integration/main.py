from pprint import pprint

from torsey.client import contactTracker
from torsey.metadata_info import MetadataInfo
from torsey.torrent_loader import decodeTorrentFile

if __name__ == "__main__":
    decodedFile = decodeTorrentFile("../../resources/test.torrent")
    metadataInfo = MetadataInfo(decodedFile)
    decodedResponse = contactTracker(metadataInfo)
    pprint(decodedResponse)
