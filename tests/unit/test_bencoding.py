import unittest

from torsey.bencoding import BdecodeError, decode, encode


class BencodingEncodeTest(unittest.TestCase):

    def testEncodeInteger(self):
        self.assertEqual(encode(0), b"i0e")
        self.assertEqual(encode(42), b"i42e")
        self.assertEqual(encode(-7), b"i-7e")

    def testEncodeInvalidInteger(self):
        with self.assertRaises(BdecodeError):
            encode(True)

    def testEncodeString(self):
        self.assertEqual(encode(b"spam"), b"4:spam")
        self.assertEqual(encode(b""), b"0:")

    def testEncodeList(self):
        self.assertEqual(encode([b"spam", b"eggs"]), b"l4:spam4:eggse")

    def testEncodeNestedList(self):
        self.assertEqual(encode([1, 2, [3]]), b"li1ei2eli3eee")

    def testEncodeDictionary(self):
        self.assertEqual(encode({b"cow": b"moo"}), b"d3:cow3:mooe")

    def testEncodeDictionarySortedKeys(self):
        self.assertEqual(encode({b"spam": b"eggs", b"cow": b"moo"}), b"d3:cow3:moo4:spam4:eggse")

    def testEncodeNestedDictionary(self):
        self.assertEqual(encode({b"spam": [b"a", b"b"]}), b"d4:spaml1:a1:bee")

    def testEncodeInvalidDictionaryKey(self):
        with self.assertRaises(BdecodeError):
            encode({1: b"foo"})

    def testEncodeInvalidType(self):
        with self.assertRaises(BdecodeError):
            encode("spam")


class BencodingDecodeTest(unittest.TestCase):
    def testDecodeInteger(self):
        self.assertEqual(decode(b"i0e"), 0)
        self.assertEqual(decode(b"i42e"), 42)
        self.assertEqual(decode(b"i-7e"), -7)

    def testInvalidInteger(self):
        with self.assertRaises(BdecodeError):
            decode(b"ie")
        with self.assertRaises(BdecodeError):
            decode(b"i-0e")

    def testDecodeString(self):
        self.assertEqual(decode(b"4:spam"), b"spam")
        self.assertEqual(decode(b"0:"), b"")

    def testInvalidStringLength(self):
        with self.assertRaises(BdecodeError):
            decode(b"a:spam")
        with self.assertRaises(BdecodeError):
            decode(b"3spam")
        with self.assertRaises(BdecodeError):
            decode(b"123")

    def testDecodeList(self):
        self.assertEqual(decode(b"l4:spam4:eggse"), [b"spam", b"eggs"])

    def testNestedList(self):
        self.assertEqual(decode(b"li1ei2eli3eee"), [1, 2, [3]])

    def testUnterminatedList(self):
        with self.assertRaises(BdecodeError):
            decode(b"l4:spam")

    def testDecodeDictionary(self):
        self.assertEqual(decode(b"d3:cow3:mooe"), {b"cow": b"moo"})

    def testNestedDictionary(self):
        self.assertEqual(decode(b"d4:spaml1:a1:bee"), {b"spam": [b"a", b"b"]})

    def testInvalidDictionaryKey(self):
        with self.assertRaises(BdecodeError):
            decode(b"di1e3:fooe")

    def testUnsortedDictionaryKey(self):
        with self.assertRaises(BdecodeError):
            decode(b"d3:foo3:bar3:aaa3:bbbe")

    def testUnterminatedDictionary(self):
        with self.assertRaises(BdecodeError):
            decode(b"d3:key5:value")

    def testInvalidPrefix(self):
        with self.assertRaises(BdecodeError):
            decode(b"x123")

    def testTrailingDataIgnoredOrError(self):
        result = decode(b"i1eJUNK")
        self.assertEqual(result, 1)


class BencodingRoundTripTest(unittest.TestCase):

    def testEncodeDecodeInteger(self):
        value = 123
        self.assertEqual(decode(encode(value)), value)

    def testEncodeDecodeNegativeInteger(self):
        value = -42
        self.assertEqual(decode(encode(value)), value)

    def testEncodeDecodeString(self):
        value = b"spam"
        self.assertEqual(decode(encode(value)), value)

    def testEncodeDecodeEmptyString(self):
        value = b""
        self.assertEqual(decode(encode(value)), value)

    def testEncodeDecodeList(self):
        value = [b"spam", 1, b"eggs"]
        self.assertEqual(decode(encode(value)), value)

    def testEncodeDecodeNestedList(self):
        value = [1, [2, [3]]]
        self.assertEqual(decode(encode(value)), value)

    def testEncodeDecodeDictionary(self):
        value = {b"cow": b"moo", b"spam": b"eggs"}
        self.assertEqual(decode(encode(value)), value)

    def testEncodeDecodeNestedDictionary(self):
        value = {b"spam": [b"a", {b"b": b"c"}]}
        self.assertEqual(decode(encode(value)), value)


if __name__ == "__main__":
    unittest.main()
