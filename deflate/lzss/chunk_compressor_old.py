from dataclasses import dataclass

_OFFSET_T = int
_LENGTH_T = int


_CONTENT_T = bytes | str


@dataclass
class EncodeResult:
    symbol: _CONTENT_T | None
    offset: _OFFSET_T | None
    length: _LENGTH_T | None


class Lzss:
    def __init__(self, window_size: int, min_repeated_string_length: int = 3):
        self.__window_size = window_size
        self.__min_repeated_string_length = min_repeated_string_length

    def compress(self, data: _CONTENT_T) -> list[EncodeResult]:
        compressor = LzssChunkCompressor(
            data=data,
            window_size=self.__window_size,
            min_repeated_string_length=self.__min_repeated_string_length
        )

        return compressor.compress()

    def decompress(self, encoded_result: list[EncodeResult]) -> _CONTENT_T:
        if not encoded_result:
            raise ValueError('Empty encoded_result')

        first_encoded = encoded_result[0]
        decompressor = LzssChunkDecompressor(type(first_encoded.symbol))

        return decompressor.decompress(encoded_result)


class LzssChunkCompressor:
    def __init__(self, *, data: _CONTENT_T, window_size: int, min_repeated_string_length: int):
        self.__data = data
        self.__window_size = window_size
        self.__l = 0
        self.__buffer_length = 0
        self.__min_repeated_string_length = min_repeated_string_length

    def compress(self) -> list[EncodeResult]:
        encoded_result = []
        position = 0

        while position < len(self.__data):
            encode_result = self.__encode_symbol(position)
            encoded_result.append(encode_result)
            if encode_result.offset is None:
                self.__shift_buffer(1)
                position += 1
                continue

            self.__shift_buffer(encode_result.length)
            position += encode_result.length

        return encoded_result

    def __encode_symbol(self, position: int) -> EncodeResult:
        r = self.__find_longest_substring_in_buffer(position)

        if r is None:
            return EncodeResult(symbol=self.__data[position], offset=None, length=None)

        length = r[0]
        offset = r[1]

        if length < self.__min_repeated_string_length:
            return EncodeResult(symbol=self.__data[position], offset=None, length=None)

        return EncodeResult(symbol=None, length=length, offset=position - offset)

    def __find_longest_substring_in_buffer(self, position: int) -> tuple[_LENGTH_T, _OFFSET_T] | None:
        cur_length = 0

        result_found_index = None

        while True:
            cur_prefix = self.__data[position: position + cur_length + 1]

            found_index = self.__buffer.find(cur_prefix)
            if found_index == -1:
                break

            cur_length += 1
            result_found_index = found_index

            if cur_length + position == len(self.__data):
                break

        if result_found_index is None:
            return None

        return cur_length, result_found_index

    def __shift_buffer(self, length: int):
        self.__buffer_length += length

        if self.__buffer_length > self.__window_size:
            delta = self.__buffer_length - self.__window_size
            self.__l += delta
            self.__buffer_length -= delta

    @property
    def __buffer(self) -> _CONTENT_T:
        return self.__data[self.__l: self.__l + self.__buffer_length]


class LzssChunkDecompressor:
    def __init__(self, content_type: type[_CONTENT_T]):
        self.__content_type = content_type

    def decompress(self, encoded_result: list[EncodeResult]) -> _CONTENT_T:
        empty_content = self.__empty_content()

        substrings = []

        total_decoded = 0
        for encoded in encoded_result:
            if encoded.symbol is not None:
                substrings.append(encoded.symbol)
                total_decoded += 1
                continue

            start = total_decoded - encoded.offset
            end = start + encoded.length
            substrings.extend(substrings[i] for i in range(total_decoded - encoded.offset, end))

            total_decoded += encoded.length

        return empty_content.join(self.__symbol_to_correct_type(s) for s in substrings)

    def __empty_content(self) -> _CONTENT_T:
        if self.__content_type == str:
            return ''

        return b''

    def __symbol_to_correct_type(self, symbol: _CONTENT_T) -> _CONTENT_T:
        if self.__empty_content() == '':
            return symbol

        symbol: int
        return symbol.to_bytes(1, byteorder='big')

