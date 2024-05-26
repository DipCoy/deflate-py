import functools
from typing import TypeVar

import math

from deflate.huffman.huffman import StaticHuffmanEncoder
from deflate.lzss.chunk_compressor import Lzss, EncodeResult


T = TypeVar('T')


def _reverse_and_unzip_dict(dict_to_reverse: dict[T, list[T]]) -> dict[T, T]:
    d = {}

    for k, vs in dict_to_reverse.items():
        for v in vs:
            d[v] = k

    return d


class DeflateChunkEncoder:
    def __init__(self, window_size: int):
        self.__window_size = window_size
        self.__bin_pow = math.ceil(math.log(window_size))

    def encode(self, string: bytes):
        lzss = Lzss(window_size=self.__window_size)
        lzss_result = lzss.compress(string)
        lengths_and_symbols_encoder = StaticHuffmanEncoder(self.__huffman_statistics_string_based_on_lengths(lzss_result))
        lengths_and_symbols_codec = lengths_and_symbols_encoder.codec()
        offsets_encoder = StaticHuffmanEncoder(self.__huffman_statistics_string_based_on_offsets(lzss_result))
        offset_codec = offsets_encoder.codec()

        result = []
        huffman_tree_lengths_and_symbols_bits = lengths_and_symbols_codec.bitwise()
        huffman_tree_offsets_bits = offset_codec.bitwise()

        result.extend([
            '{:016b}'.format(len(huffman_tree_lengths_and_symbols_bits)),
            huffman_tree_lengths_and_symbols_bits,
        ])

        result.extend([
            '{:016b}'.format(len(huffman_tree_offsets_bits)),
            huffman_tree_offsets_bits,
        ])

        for lzss_encoded in lzss_result:
            lzss_encoded_bits = self._encode_lzss_result(lzss_encoded, lengths_and_symbols_codec, offset_codec)
            result.append(lzss_encoded_bits)

        return ''.join(result)

    def _encode_lzss_result(self, r: EncodeResult, length_and_symbols_codec, offset_codec) -> str:
        if r.symbol is not None:
            return '0' + length_and_symbols_codec.encode(r.symbol)

        return '1' + self._encode_length_offset(r, length_and_symbols_codec=length_and_symbols_codec, offset_codec=offset_codec)

    def _encode_length_offset(self, r: EncodeResult, *, length_and_symbols_codec, offset_codec) -> str:
        length_code = self._encode_length(r.length, length_and_symbols_codec)
        offset_code = self._encode_offset(r.offset, offset_codec)

        return length_code + offset_code

    def _encode_length(self, length: int, codec) -> str:
        base_length_code = self.__huffman_reverse_lengths_table[length]
        min_bound_for_base_length_code = self.__huffman_lengths_table[base_length_code][0]
        length_extra_bits = self.__required_extra_bits_for_base_length_code(base_length_code)
        if length_extra_bits == 0:
            return codec.encode(base_length_code)

        base_length_huffman_code = codec.encode(base_length_code)
        delta_bin_code = ('{:0' + f'{length_extra_bits}' + 'b}').format(length - min_bound_for_base_length_code)

        return base_length_huffman_code + delta_bin_code

    def _encode_offset(self, offset: int, codec) -> str:
        base_offset_code = self.__hugman_reverse_offset_table[offset]
        min_bound_for_base_offset_code = self.__huffman_offset_table[base_offset_code][0]
        length_extra_bits = self.__required_extra_bits_for_base_offset_code(base_offset_code)
        if length_extra_bits == 0:
            return codec.encode(base_offset_code)

        base_offset_huffman_code = codec.encode(base_offset_code)
        delta_bin_code = ('{:0' + f'{length_extra_bits}' + 'b}').format(offset - min_bound_for_base_offset_code)

        return base_offset_huffman_code + delta_bin_code


    def __huffman_statistics_string_based_on_lengths(self, lzss_result: list[EncodeResult]) -> list[int]:
        r = [256, 286, 287]
        symbols_for_encoding = set(r)

        for lzss_encoded in lzss_result:
            if lzss_encoded.symbol is not None:
                r.append(lzss_encoded.symbol)
                continue

            length_code = self.__huffman_reverse_lengths_table[lzss_encoded.length]
            r.append(length_code)

        for code in range(0, 288):
            if code not in symbols_for_encoding:
                symbols_for_encoding.add(code)
                r.append(code)

        return r

    def __huffman_statistics_string_based_on_offsets(self, lzss_result: list[EncodeResult]) -> list[int]:
        r = []

        used_codes = set()

        for lzss_encoded in lzss_result:
            if lzss_encoded.offset is None:
                continue

            base_offset_code = self.__hugman_reverse_offset_table[lzss_encoded.offset]
            r.append(base_offset_code)
            used_codes.add(base_offset_code)

        for offset_code in self.__huffman_offset_table.keys():
            if offset_code not in used_codes:
                used_codes.add(offset_code)
                r.append(offset_code)

        return r

    @functools.cached_property
    def __huffman_lengths_table(self) -> dict[int, list[int]]:
        d = {
            257 + i - 3: [i] for i in range(3, 10 + 1)
        }

        d[265] = [11, 12]
        d[266] = [13, 14]
        d[267] = [15, 16]
        d[268] = [17, 18]
        d[269] = [19, 22]
        d[270] = list(range(23, 27))
        d[271] = list(range(27, 31))
        d[272] = list(range(31, 35))
        d[273] = list(range(35, 43))
        d[274] = list(range(43, 51))
        d[275] = list(range(51, 59))
        d[276] = list(range(59, 67))
        d[277] = list(range(67, 83))
        d[278] = list(range(83, 99))
        d[279] = list(range(99, 115))
        d[280] = list(range(115, 131))
        d[281] = list(range(131, 163))
        d[282] = list(range(163, 195))
        d[283] = list(range(195, 227))
        d[284] = list(range(227, 258))
        d[285] = [258]
        return d

    def __required_extra_bits_for_base_length_code(self, base_code: int) -> int:
        if 257 <= base_code <= 264:
            return 0

        if base_code == 285:
            return 0

        delta = base_code - 265

        return delta // 4 + 1

    def __required_extra_bits_for_base_offset_code(self, base_code: int) -> int:
        if 0 <= base_code <= 3:
            return 0

        delta = base_code - 4

        return delta // 2 + 1

    @functools.cached_property
    def __huffman_reverse_lengths_table(self):
        return _reverse_and_unzip_dict(self.__huffman_lengths_table)

    @functools.cached_property
    def __huffman_offset_table(self) -> dict[int, list[int]]:
        current_offset = 5
        current_code = 4
        extra_bits = 0

        table = {0: [1], 1: [2], 2: [3], 3: [4]}

        while current_offset <= self.__window_size:
            if current_code % 2 == 0:
                extra_bits += 1
            table[current_code] = []
            for i in range(2**extra_bits):
                if current_offset > self.__window_size:
                    break
                table[current_code].append(current_offset)
                current_offset += 1

            current_code += 1

        return table

    @functools.cached_property
    def __hugman_reverse_offset_table(self) -> dict[int, int]:
        return _reverse_and_unzip_dict(self.__huffman_offset_table)


print(DeflateChunkEncoder(65536).encode(b'BanBanBanBanBanBanBanBanBan'))


