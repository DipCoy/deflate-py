from heapq import heappush, heappop
from collections import Counter
from typing import Iterable
from collections import abc


class Codec:
    def __init__(self):
        self.letters = {}
        self.codes = {}

    def update(self, letter, code):
        self.letters[code] = letter
        self.codes[letter] = code

    def encode(self, s):
        if isinstance(s, abc.Iterable):
            return ''.join(self.codes[letter] for letter in s)

        return self.codes[s]

    def _decode(self, s):
        code = ''

        for c in s:
            code += c

            if code in self.letters:
                yield self.letters[code]
                code = ''

        assert code == ''

    def decode(self, s):
        return ''.join(self._decode(s))

    def bitwise(self):
        encoded_codes = []
        for symbol in sorted(self.codes.keys()):
            code = self.codes[symbol]
            code_length = len(code)
            code_length_bits = '{:08b}'.format(code_length)
            encoded_codes.append(code_length_bits+code)

        return ''.join(encoded_codes)

    def from_bitwise(self, encoded: str, *, alphabet):
        current_alphabet_index = 0
        decoded_codes = {}
        cursor = 0
        while cursor < len(encoded):
            code_length = int(encoded[cursor: cursor + 8], 2)
            cursor += 8

            code = encoded[cursor: cursor + code_length]
            decoded_codes[alphabet[current_alphabet_index]] = code

            cursor += code_length
            current_alphabet_index += 1

        return decoded_codes


_HUFFMAN_CODES_T = dict[str, str]


class StaticHuffmanEncoder:
    def __init__(self, statistics_string: Iterable):
        self.__statistics_string = statistics_string
        self.__codes = self.__huffman_codes()

    @property
    def codes(self) -> _HUFFMAN_CODES_T:
        return self.__codes

    def codec(self) -> Codec:
        codec = Codec()

        for letter, code in self.__codes.items():
            codec.update(letter, code)

        return codec

    def __huffman_codes(self):
        frequencies = Counter(self.__statistics_string)
        if len(frequencies) == 1:
            letter, = frequencies
            return {letter: '0'}

        queue = []
        res = {letter: '' for letter in frequencies}

        for letter, frequency in frequencies.items():
            heappush(queue, (frequency, (letter,)))

        while len(queue) > 1:
            first_freq, first_letters = heappop(queue)
            second_freq, second_letters = heappop(queue)

            for letter in first_letters:
                res[letter] = '0' + res[letter]

            for letter in second_letters:
                res[letter] = '1' + res[letter]

            heappush(
                queue,
                (
                    first_freq + second_freq,
                    tuple(sorted((*first_letters, *second_letters)))
                )
            )

        return res


class StaticHuffmanDecoder:
    def __init__(self, codes: _HUFFMAN_CODES_T):
        self.__codes = codes
        self.__letters = {code: symbol for symbol, code in self.__codes.items()}

    def decode(self, bin_string: str) -> str:
        codec = Codec()
        codec.codes = self.__codes
        codec.letters = self.__letters
        return codec.decode(bin_string)


def tree_encode(tree):
    return [len(node) for node in tree]
