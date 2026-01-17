class MetadataInfoParseError(Exception):
    pass


def expectType(value, expectedType):
    if not isinstance(value, expectedType):
        raise MetadataInfoParseError(
            f"Expected '{value}' of type '{expectedType.__name__}', found '{type(value).__name__}'.")


def expectKey(container: dict, key: bytes):
    if key not in container:
        raise MetadataInfoParseError(f"Expected key '{key}' in dictionary {container}.")


def decodeBytes(data):
    expectType(data, bytes)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise MetadataInfoParseError(f"Tracker URL is not valid UTF-8 '{data!r}'.")


class File:
    def __init__(self, length: int, path: list):
        self.length = length
        self.path = path


class MetadataInfo:
    def __init__(self, data: dict):
        self.currentTier = 0
        self.currentAnnounceInTier = 0
        expectType(data, dict)
        if (key := b"announce-list") in data:
            # Reference: <https://bittorrent.org/beps/bep_0012.html>
            self.announce = None
            rawAnnouncesList = data[key]
            expectType(rawAnnouncesList, list)
            announcesList = []
            for rawAnnounces in rawAnnouncesList:
                expectType(rawAnnounces, list)
                announces = []
                for announce in rawAnnounces:
                    announces.append(decodeBytes(announce))
                announcesList.append(announces)
            self.announceList = announcesList
        elif (key := b"announce") in data:
            self.announce = decodeBytes(data[key])
            self.announceList = None
        else:
            raise MetadataInfoParseError("Torrent must contain 'announce' or 'announce-list'.")

        if (key := b"info") in data:
            self.info = data[key]
        else:
            raise MetadataInfoParseError("Torrent must contain key 'info'.")

        if (key := b"length") in self.info:
            expectType(self.info[key], int)
            self.length = self.info[key]
            self.files = None
        elif (key := b"files") in self.info:
            expectType(self.info[key], list)
            # TODO: files-dictionary can be empty.
            files = []
            for fileDict in self.info[key]:
                expectType(fileDict, dict)
                expectKey(fileDict, b"length")
                length = fileDict[b"length"]
                expectType(length, int)
                expectKey(fileDict, b"path")
                rawPath = fileDict[b"path"]
                expectType(rawPath, list)
                path = [decodeBytes(element) for element in rawPath]
                files.append({"length": length, "path": path})
            self.length = None
            self.files = files
        else:
            raise MetadataInfoParseError("Torrent must contain 'length' or 'files' inside 'info'.")

    def totalLength(self) -> int:
        if self.length is not None:
            return self.length
        elif self.files is not None:
            return sum(file["length"] for file in self.files)
        else:
            return 0

    def getAnnounce(self):
        if self.announce is not None:
            return self.announce
        if self.announceList is not None:
            if self.currentTier >= len(self.announceList):
                return None
            tier = self.announceList[self.currentTier]
            if self.currentAnnounceInTier >= len(tier):
                self.currentTier += 1
                return self.getAnnounce()
            return tier[self.currentAnnounceInTier]
        return None

    def shiftAnnounce(self):
        self.currentAnnounceInTier += 1
