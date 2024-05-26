import logging

from deflate.huffman_encoder import DeflateHuffmanEncoder


logger = logging.getLogger(__name__)

NON_COMPRESSED_BTYPE = '00'
COMPRESSED_HUFFMAN_BTYPE = '10'


class DeflateLikeEncoder:
    def __init__(self, window_size: int = 32768):
        self.__huffman_encoder = DeflateHuffmanEncoder(window_size)

    def encode(self, chunk: bytes) -> str:
        huffman_encoded = self.__compress_huffman_block(chunk)
        non_compressed = self.__non_compress_block(chunk)

        logger.debug(f'{len(huffman_encoded)=}, {len(non_compressed)=}')

        if len(huffman_encoded) < len(non_compressed):
            logger.debug('Good encoded!')
            return huffman_encoded

        logger.debug('Raw data :(')
        return non_compressed

    def __compress_huffman_block(self, chunk: bytes) -> str:
        encoded_chunk_bits = self.__huffman_encoder.encode(chunk)
        return COMPRESSED_HUFFMAN_BTYPE + '{:016b}'.format(len(encoded_chunk_bits)) + encoded_chunk_bits

    def __non_compress_block(self, chunk: bytes) -> str:
        bits_from_bytes = [
            '{:016b}'.format(byte)
            for byte in chunk
        ]

        bits = ''.join(bits_from_bytes)
        return NON_COMPRESSED_BTYPE + '{:016b}'.format(len(bits)) + bits
