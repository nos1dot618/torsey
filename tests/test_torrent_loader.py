import unittest
from torsey.torrent_loader import decodeTorrentURL


class TestTorrentLoader(unittest.TestCase):
    def testDecodeTorrentURL(self):
        decodedTorrent = decodeTorrentURL(
            "https://sample-file.bazadanni.com/download/applications/torrent/sample.torrent")
        self.assertIn(b"announce", decodedTorrent)
        self.assertIn(b"info", decodedTorrent)


if __name__ == "__main__":
    unittest.main()
