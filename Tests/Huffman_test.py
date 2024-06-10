import unittest
import Huffman
import string
import random


class MyTestCase(unittest.TestCase):
    @staticmethod
    def _generate_word(length):
        symbols = [*string.ascii_letters] + ['\n', '\r', '\t']
        result = ''
        for _ in range(length):
            result += random.choice(symbols)
        return result

    def _check_coding(self, text):
        """
            Проверяет, чтобы текст кодировался
            и раскодировался без потерь информации
        :return:
        """
        encoding_table = Huffman.get_encoding_table(text)
        decoding_table = Huffman.swap_dictionary(encoding_table)
        binary_code = Huffman.encode(text, encoding_table)
        decoded_text = Huffman.decode(binary_code, decoding_table)
        self.assertEqual(text, decoded_text)

    def test_special_symbols(self):
        self._check_coding("\n")
        self._check_coding("\r")
        self._check_coding("\t")
        self._check_coding("\n\n\n\r\t")

    def test_invalid_table(self):
        invalid_encoding_table = dict()
        invalid_decoding_table = dict()
        text = self._generate_word(30)
        self.assertRaises(ValueError, Huffman.encode,
                          text, invalid_encoding_table)
        self.assertRaises(ValueError, Huffman.decode,
                          text, invalid_decoding_table)

    def test_empty(self):
        self._check_coding("")

    def test_random(self):
        self._check_coding(self._generate_word(20))


if __name__ == '__main__':
    unittest.main()
