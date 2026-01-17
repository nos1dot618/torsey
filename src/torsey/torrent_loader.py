import tempfile
from urllib.request import urlopen

from torsey.bencoding import BdecodeError, decode
from torsey.logger import info


def decodeTorrentFile(path: str):
    try:
        with open(path, "rb") as file:
            rawData = file.read()
        decodedData = decode(rawData)
        return decodedData
    except FileNotFoundError:
        raise RuntimeError(f"File not found '{path}'.")
    except BdecodeError as e:
        raise RuntimeError(f"Invalid torrent file: '{e}'.")


def decodeTorrentURL(url: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".torrent") as tmp:
        with urlopen(url) as response:
            while True:
                chunk = response.read(4096)
                if not chunk:
                    break
                tmp.write(chunk)
    info(f"Downloaded torrent-file from URL '{url}' to temporary-path '{tmp.name}'.")
    return decodeTorrentFile(tmp.name)
