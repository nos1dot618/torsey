class PeerInfoParseError(Exception):
    pass


def expectType(value, expectedType):
    if not isinstance(value, expectedType):
        raise PeerInfoParseError(
            f"Expected '{value}' of type '{expectedType.__name__}', found '{type(value).__name__}'.")


def expectKey(container: dict, key: bytes):
    if key not in container:
        raise PeerInfoParseError(f"Expected key '{key}' in dictionary {container}.")


def decodeBytes(data):
    expectType(data, bytes)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise PeerInfoParseError(f"{data!r} is not valid UTF-8 .")


class Peer:
    def __init__(self, ip: str, peerID: bytes, port: int):
        self.ip = ip
        self.peerID = peerID
        self.port = port

    def __str__(self):
        return f"Peer({self.ip}, {self.peerID}, {self.port})"

    def __repr__(self):
        return self.__str__()


class PeerInfo:
    def __init__(self, data: dict):
        expectType(data, dict)
        expectKey(data, b"interval")
        expectType(data[b"interval"], int)
        self.interval = data[b"interval"]
        expectKey(data, b"peers")
        self.peers = []
        for rawPeer in data[b"peers"]:
            expectType(rawPeer, dict)
            expectKey(rawPeer, b"ip")
            expectType(rawPeer[b"ip"], bytes)
            expectKey(rawPeer, b"peer id")
            expectType(rawPeer[b"peer id"], bytes)
            expectKey(rawPeer, b"port")
            expectType(rawPeer[b"port"], int)
            self.peers.append(Peer(decodeBytes(rawPeer[b"ip"]), rawPeer[b"peer id"], rawPeer[b"port"]))

    def __repr__(self):
        return {
            "interval": self.interval,
            "peers": self.peers
        }
