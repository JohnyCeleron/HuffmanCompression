import heapq


class Node:
    def __init__(self, weight, value=None, left=None, right=None, code=''):
        self.weight = weight
        self.value = value
        self.left = left
        self.right = right
        self.code = code

    def __gt__(self, other):
        if not isinstance(other, Node):
            raise ValueError("The other object must be of the Node type")
        return self.weight > other.weight

    def __lt__(self, other):
        if not isinstance(other, Node):
            raise ValueError("The other object must be of the Node type")
        return self.weight < other.weight

    def __eq__(self, other):
        if not isinstance(other, Node):
            raise ValueError("The other object must be of the Node type")
        return self.weight == other.weight

    def __hash__(self):
        return hash((self.weight, self.value, self.left, self.right))

    def __str__(self):
        return f'{self.value} {self.weight}'


def decode(binary_code, decoding_dictionary, fileName='', has_progressBar=True):
    """
        Раскодирует бинарный код
    :param fileName: Файл, который будет разархивироваться
    :param has_progressBar: Надо ли показывать прогресс бар
    :param binary_code:
    :param decoding_dictionary: таблица, по которой происходит раскодировка
    :return: раскодированный текст
    """
    def print_progress():
        if has_progressBar:
            print(f'{(pointer / len(binary_code)) * 100 : 3.2f}% {fileName}', end='\r')


    pointer = 0
    decoding_text = ''
    max_len_code = 0 if len(decoding_dictionary) == 0 else \
        len(max(decoding_dictionary.keys(), key = lambda i: len(i)))
    while pointer < len(binary_code):
        for i in range(1, max_len_code + 1):
            end_prefix = min(len(binary_code), pointer + i)
            prefix = binary_code[pointer: end_prefix]
            if prefix in decoding_dictionary:
                pointer += len(prefix)
                decoding_text += decoding_dictionary[prefix]
                print_progress()
                break
        else:
            raise ValueError(f"Invalid decoding dictionary")
    return decoding_text


def encode(text, encoding_dictionary, fileName='', has_progressBar=True):
    """
        Кодирует текст
    :param has_progressBar: Надо ли показывать прогресс бар
    :param fileName: Файл, который будет архивироваться
    :param text:
    :param encoding_dictionary: таблица, по которой происходит кодировка
    :return: закодированный текст в формате бинарного кода
    """
    def print_progress():
        if has_progressBar:
            print(f'{(count / len(text)) * 100 : 3.2f}% {fileName}', end='\r')

    binary_code = ''
    count = 1
    for c in text:
        if c not in encoding_dictionary.keys():
            raise ValueError("Invalid encoding dictionary")
        binary_code += encoding_dictionary[c]
        print_progress()
        count += 1
    return binary_code


def get_encoding_table(text):
    """
        С помощью алгоритма Хаффмана кодирует каждый символ
    :param text: текст, символы которого надо закодировать
    :return: словарь, где ключ - это символ, а значение - бинарный код
    """
    queue = []
    frequency_dictionary = _get_frequency_dictionary(text)
    for character, count in frequency_dictionary.items():
        heapq.heappush(queue, Node(count, character))

    if len(queue) == 0:
        return dict()
    elif len(queue) == 1:
        return {queue[0].value: "0"}

    while len(queue) > 1:
        first = heapq.heappop(queue)
        second = heapq.heappop(queue)
        node = Node(first.weight + second.weight, left=first, right=second)
        heapq.heappush(queue, node)
    return _walk_through_Huffman_tree(queue[0])


def swap_dictionary(dictionary):
    swapped_dictionary = dict()
    for key, value in dictionary.items():
        swapped_dictionary[value] = key
    return swapped_dictionary


def _get_frequency_dictionary(text):
    return {x: text.count(x) for x in set(text)}


def _walk_through_Huffman_tree(root):
    stack = [root]
    encode_characters = dict()
    while len(stack) > 0:
        node = stack.pop()
        if node.left is not None:
            node.left.code = node.code + '1'
            stack.append(node.left)
        if node.right is not None:
            node.right.code = node.code + '0'
            stack.append(node.right)
        if node.right is None and node.left is None:
            encode_characters[node.value] = node.code
    return encode_characters


if __name__ == '__main__':
    text = 'asdflllds;'
    print(get_encoding_table(text))
