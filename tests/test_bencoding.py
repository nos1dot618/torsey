import unittest
from torsey.bencoding import BencodeError, decode


class BencodingTest(unittest.TestCase):
    def testDecodeInteger(self):
        self.assertEqual(decode(b"i0e"), 0)
        self.assertEqual(decode(b"i42e"), 42)
        self.assertEqual(decode(b"i-7e"), -7)

    def testInvalidInteger(self):
        with self.assertRaises(BencodeError):
            decode(b"ie")
        with self.assertRaises(BencodeError):
            decode(b"i-0e")

    def testDecodeString(self):
        self.assertEqual(decode(b"4:spam"), b"spam")
        self.assertEqual(decode(b"0:"), b"")

    def testInvalidStringLength(self):
        with self.assertRaises(BencodeError):
            decode(b"a:spam")
        with self.assertRaises(BencodeError):
            decode(b"3spam")
        with self.assertRaises(BencodeError):
            decode(b"123")

    def testDecodeList(self):
        self.assertEqual(decode(b"l4:spam4:eggse"), [b"spam", b"eggs"])

    def testNestedList(self):
        self.assertEqual(decode(b"li1ei2eli3eee"), [1, 2, [3]])

    def testUnterminatedList(self):
        with self.assertRaises(BencodeError):
            decode(b"l4:spam")

    def testDecodeDictionary(self):
        self.assertEqual(decode(b"d3:cow3:mooe"), {b"cow": b"moo"})

    def testNestedDictionary(self):
        self.assertEqual(decode(b"d4:spaml1:a1:bee"), {b"spam": [b"a", b"b"]})

    def testInvalidDictionaryKey(self):
        with self.assertRaises(BencodeError):
            decode(b"di1e3:fooe")

    def testUnsortedDictionaryKey(self):
        with self.assertRaises(BencodeError):
            decode(b"d3:foo3:bar3:aaa3:bbbe")

    def testUnterminatedDictionary(self):
        with self.assertRaises(BencodeError):
            decode(b"d3:key5:value")

    def testInvalidPrefix(self):
        with self.assertRaises(BencodeError):
            decode(b"x123")

    def testTrailingDataIgnoredOrError(self):
        result = decode(b"i1eJUNK")
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
