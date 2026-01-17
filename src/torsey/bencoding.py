class BencodeError(Exception):
    pass


class Stream:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def next(self):
        if self.pos >= len(self.data):
            raise StopIteration
        char = self.data[self.pos]
        self.pos += 1
        return char

    def peek(self):
        if self.pos >= len(self.data):
            raise StopIteration
        return self.data[self.pos]


def encode(data) -> bytes:
    if isinstance(data, bool):
        # Needed because boolean is a subtype of integer.
        raise BencodeError("Invalid type 'bool'.")
    if isinstance(data, int):
        return encodeInteger(data)
    if isinstance(data, list):
        return encodeList(data)
    if isinstance(data, dict):
        return encodeDictionary(data)
    if isinstance(data, bytes):
        return encodeString(data)
    raise BencodeError(f"Invalid type '{type(data)}'.")


def encodeInteger(data: int) -> bytes:
    return b"i" + str(data).encode() + b"e"


def encodeList(data: list) -> bytes:
    return b"l" + b"".join(encode(element) for element in data) + b"e"


def encodeDictionary(data: dict) -> bytes:
    encodedItems = []
    for key in sorted(data.keys()):
        if not isinstance(key, bytes):
            raise BencodeError(f"Invalid key '{key}', dictionary-key must be bytes.")
        encodedItems.append(encodeString(key))
        encodedItems.append(encode(data[key]))
    return b"d" + b"".join(encodedItems) + b"e"


def encodeString(data: bytes) -> bytes:
    return str(len(data)).encode() + b":" + data


def decode(data: bytes):
    return decodeNext(Stream(data))


def decodeNext(stream: Stream):
    try:
        char = stream.peek()
    except StopIteration:
        raise BencodeError("Unexpected end of stream.")
    if char == ord(b"i"):
        stream.next()
        return decodeInteger(stream)
    if char == ord(b"l"):
        stream.next()
        return decodeList(stream)
    if char == ord(b"d"):
        stream.next()
        return decodeDictionary(stream)
    if ord(b"0") <= char <= ord(b"9"):
        return decodeString(stream)
    raise BencodeError(f"Invalid bencode prefix '{chr(char)}'.")


def decodeInteger(stream: Stream) -> int:
    # FIXME: This accepts '-0', which is invalid according to the BEP-3 specification.
    digits = []
    while True:
        try:
            char = stream.next()
        except StopIteration:
            raise BencodeError("Unterminated integer.")
        if char == ord(b"e"):
            if len(digits) == 0:
                raise BencodeError(f"Empty integer.")
            return int("".join(digits))
        digits.append(chr(char))


def decodeList(stream: Stream) -> list:
    items = []
    while True:
        try:
            char = stream.peek()
        except StopIteration:
            raise BencodeError(f"Unterminated list '{items}'.")
        if char == ord(b"e"):
            stream.next()
            return items
        items.append(decodeNext(stream))


def decodeDictionary(stream: Stream) -> dict:
    items = dict()
    previousKey = None
    while True:
        try:
            char = stream.peek()
        except:
            raise BencodeError("Unterminated dictionary.")
        if char == ord(b"e"):
            stream.next()
            return items
        key = decodeNext(stream)
        if not isinstance(key, bytes):
            raise BencodeError(f"Invalid key '{key}', dictionary-key must be bytes.")
        if previousKey is not None:
            if key < previousKey:
                raise BencodeError(f"Dictionary-keys are not sorted lexicographically. Found '{previousKey}' > '{key}'")
        previousKey = key
        value = decodeNext(stream)
        items[key] = value


def decodeString(stream: Stream) -> bytes:
    digits = []
    while True:
        try:
            char = stream.next()
        except StopIteration:
            raise BencodeError("Unterminated string-length.")
        if char == ord(b":"):
            break
        if ord(b"0") <= char <= ord(b"9"):
            digits.append(chr(char))
            continue
        raise BencodeError(f"Invalid character found '{chr(char)}' in string-length declaration.")
    length = int("".join(digits))
    return bytes(stream.next() for _ in range(length))
