import random
import string

import pytest

from src import Huffman
from src.Huffman import Node


class TestNode:

    @pytest.mark.parametrize('my_node,other_node,expected', [
        (Node(5), Node(5), False),
        (Node(5), Node(1), True),
        (Node(6), Node(5), True)
    ])
    def test_great(self, my_node, other_node, expected):
        assert (my_node > other_node) == expected

    @pytest.mark.parametrize('my_node,other_node,expected', [
        (Node(5), Node(5), False),
        (Node(5), Node(1), False),
        (Node(6), Node(7), True)
    ])
    def test_less(self, my_node, other_node, expected):
        assert (my_node < other_node) == expected

    @pytest.mark.parametrize('my_node,other_node', [
        (Node(5), None), (Node(5), str)
    ])
    def test_type_error(self, my_node, other_node):
        with pytest.raises(TypeError) as error1:
            my_node > other_node
        with pytest.raises(TypeError) as error2:
            my_node < other_node
        with pytest.raises(TypeError) as error3:
            my_node == other_node
        assert str(error1.value) == "The other object must be of the Node type"
        assert str(error2.value) == "The other object must be of the Node type"
        assert str(error3.value) == "The other object must be of the Node type"

    @pytest.mark.parametrize('my_node,other_node,expected', [
        (Node(5), Node(5), True),
        (Node(5), Node(1), False),
        (Node(6), Node(7), False)
    ])
    def test_great(self, my_node, other_node, expected):
        assert (my_node == other_node) == expected


def _generate_word(length):
    symbols = [*string.ascii_letters] + ['\n', '\r', '\t']
    result = ''
    for _ in range(length):
        result += random.choice(symbols)
    return result


def _check_coding(text):
    """
        Проверяет, чтобы текст кодировался
        и раскодировался без потерь информации
    :return:
    """
    encoding_table = Huffman.get_encoding_table(text)
    decoding_table = Huffman.swap_dictionary(encoding_table)
    binary_code = Huffman.encode(text, encoding_table, has_progressBar=False)
    decoded_text = Huffman.decode(binary_code, decoding_table,
                                  has_progressBar=False)
    assert text == decoded_text


@pytest.mark.parametrize('special_symbols', [
    '\n', '\r', '\t', '\n\n\n\r\t'
])
def test_special_symbols(special_symbols):
    _check_coding(special_symbols)


def test_invalid_table():
    invalid_encoding_table = dict()
    invalid_decoding_table = dict()
    text = _generate_word(30)
    with pytest.raises(ValueError):
        Huffman.encode(text, invalid_encoding_table)
    with pytest.raises(ValueError):
        Huffman.encode(text, invalid_decoding_table)


def test_empty():
    _check_coding('')


@pytest.mark.parametrize('length', [
    10, 20, 30, 40, 0
])
def test_random(length):
    _check_coding(_generate_word(length))


if __name__ == '__main__':
    pass
