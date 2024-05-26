from typing import Generator


_OFFSET_T = int
_LENGTH_T = int


class SimpleWindowBuffer:
    def __init__(self, data_generator: Generator[bytes], *, size: int):
        self.__data_generator = data_generator
        self.__size = size
        self.__buffer = b''
        self.__fill()

    def shift(self, length: int) -> None:
        self.__buffer = self.__data_generator[length:]
        self.__fill()

    def find_match(self, position: int) -> (_OFFSET_T, _LENGTH_T):
        ...

    def __fill(self) -> None:
        need_to_read = self.__size - len(self.__buffer)
        new_data = self.__read_data(need_to_read)
        self.__buffer += new_data

    def __read_data(self, n: int) -> bytes:
        bytes_array = []

        for _, byte in zip(range(n), self.__data_generator):
            bytes_array.append(byte)

        return b''.join(bytes_array)

