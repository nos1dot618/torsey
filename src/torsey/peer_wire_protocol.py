# Reference: <https://wiki.theory.org/BitTorrentSpecification>

import struct


class PeerConnectionState:
    def __init__(self):
        self.amChoking = True
        self.amInterested = False
        self.peerChoking = True
        self.peerInterested = False

    def canDownload(self):
        return self.amInterested and not self.peerChoking

    def canUpload(self):
        return self.peerInterested and not self.amChoking


def buildCommandKeepAlive() -> bytes:
    return struct.pack(">I", 0)


def buildCommandChoke() -> bytes:
    return struct.pack(">I", 1) + struct.pack(">B", 0)


def buildCommandUnchoke() -> bytes:
    return struct.pack(">I", 1) + struct.pack(">B", 1)


def buildCommandInterested() -> bytes:
    return struct.pack(">I", 1) + struct.pack(">B", 2)


def buildCommandNotInterested() -> bytes:
    return struct.pack(">I", 1) + struct.pack(">B", 3)


def buildCommandHave(pieceIndex: bytes) -> bytes:
    assert len(pieceIndex) == 16
    return struct.pack(">I", 5) + struct.pack(">B", 4) + pieceIndex


def buildCommandBitField() -> bytes:
    # TODO: Complete this
    pass


def buildCommandRequest(index: bytes, begin: bytes, length: bytes) -> bytes:
    # The usage of this command is disputed, refer: <https://wiki.theory.org/Talk_BitTorrentSpecification.html#Messages:_request>.
    assert len(index) == 4
    assert len(begin) == 4
    assert len(length) == 4
    return struct.pack(">I", 13) + struct.pack(">B", 6) + index + begin + length


def buildCommandPiece(index: bytes, begin: bytes, piece: bytes) -> bytes:
    assert len(index) == 4
    assert len(begin) == 4
    return struct.pack(">I", 9 + len(piece)) + struct.pack(">B", 7) + index + begin + piece


def buildCommandCancel(index: bytes, begin: bytes, length: bytes) -> bytes:
    assert len(index) == 4
    assert len(begin) == 4
    assert len(length) == 4
    return struct.pack(">I", 13) + struct.pack(">B", 8) + index + begin + length


def buildCommandPort(listenPort: bytes) -> bytes:
    assert len(listenPort) == 2
    return struct.pack(">I", 3) + struct.pack(">B", 9) + listenPort
