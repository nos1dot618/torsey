from torsey.client import contactTracker, talkToPeer
from torsey.metadata_info import MetadataInfo
from torsey.torrent_loader import decodeTorrentFile

if __name__ == "__main__":
    decodedFile = decodeTorrentFile("../../resources/test.torrent")
    metadataInfo = MetadataInfo(decodedFile)
    peerInfo = contactTracker(metadataInfo)
    # talkToPeer(metadataInfo, peerInfo)
