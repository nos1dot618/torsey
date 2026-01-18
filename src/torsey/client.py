import os
import socket
import struct
import urllib.parse
from urllib.error import URLError
from urllib.request import urlopen

from torsey.bencoding import decode
from torsey.logger import info, warning
from torsey.metadata_info import MetadataInfo
from torsey.peer_info import PeerInfo, Peer

DEFAULT_PORT = 6881
PROTOCOL_STRING = b"BitTorrent protocol"
TCP_TIMEOUT = 5


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


def contactTracker(metadataInfo: MetadataInfo, port: int = DEFAULT_PORT) -> PeerInfo:
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
    return PeerInfo(decode(data))


def receiveExact(sock: socket.socket, n: int) -> bytes:
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed by the peer")
        data += chunk
    return data


def handshake(metadataInfo: MetadataInfo, peer: Peer, sock: socket.socket) -> bytes:
    sock.sendall((
            struct.pack("B", len(PROTOCOL_STRING)) +
            PROTOCOL_STRING +
            b"\x00\x00\x00\x00\x00\x10\x00\x00" +  # Extension Protocol.
            metadataInfo.getInfoHash() +
            peer.peerID
    ))
    protocolLength = struct.unpack("!B", receiveExact(sock, 1))[0]
    assert protocolLength == len(PROTOCOL_STRING)
    protocol = receiveExact(sock, protocolLength)
    assert protocol == PROTOCOL_STRING
    receiveExact(sock, 8)  # Ignore 8 reserved bytes
    infoHash = receiveExact(sock, 20)
    assert metadataInfo.getInfoHash() == infoHash
    return receiveExact(sock, 20)


def talkToPeer(metadataInfo: MetadataInfo, peerInfo: PeerInfo):
    assert peerInfo is not None
    assert peerInfo.peers is not None
    assert len(peerInfo.peers) > 0
    for peer in peerInfo.peers:
        try:
            sock = socket.create_connection((peer.ip, peer.port), timeout=TCP_TIMEOUT)
            sock.settimeout(TCP_TIMEOUT)
            info(f"Connected to peer '{peer.ip}:{peer.port}' with ID '{peer.peerID}'")
            remotePeerID = handshake(metadataInfo, peer, sock)
        except (TimeoutError, OSError) as e:
            warning(f"Failed to connect to peer '{peer.ip}:{peer.port}' with ID '{peer.peerID}'")
            continue
        raise RuntimeError("No usable peers found")
