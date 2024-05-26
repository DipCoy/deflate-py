import functools
import itertools
import math
import struct
import time
from multiprocessing import Pool

from decapitalization.decapitalizer import Decapitalizer
from decapitalization.rules import FirstTextLetterRule, UpperLetterAfterTwoUpperLettersRule, \
    UpperLetterAfterFullStopRule
from deflate.encoder import DeflateLikeEncoder
from deflate.utils import read_file_by_chunks


def get_chunks(file_path: str, chunk_size: int) -> list[bytes]:
    return list(read_file_by_chunks(file_path, chunk_size))


def compress_chunk(chunk: bytes, *, window_size: int, decapitalize: bool):
    encoder = DeflateLikeEncoder(window_size)

    if decapitalize:
        rules = [
            FirstTextLetterRule(),
            UpperLetterAfterFullStopRule(),
            UpperLetterAfterTwoUpperLettersRule(),
        ]

        decapitalizer = Decapitalizer(rules)
        chunk_string = chunk.decode('utf-8')
        chunk, deviations = decapitalizer.decapitalize(chunk_string)
        deviations_as_bytes = b''.join([struct.pack('>H', d) for d in deviations])

        chunk = chunk.encode('utf-8') + deviations_as_bytes

    return encoder.encode(chunk)


def compress_file_print_stat(file_path: str, *, chunk_size: int):
    chunks = get_chunks(file_path, chunk_size)
    file_size_bytes = sum(len(ch) for ch in chunks)

    window_size_params = [16384, 32768, 65536]
    decapitalize_params = [False, True]

    for window_size, decapitalize in itertools.product(window_size_params, decapitalize_params):
        compress_function = functools.partial(compress_chunk, window_size=window_size, decapitalize=decapitalize)

        start_file_processing = time.time()

        with Pool() as pool:
            compressed_chunks = pool.map(compress_function, chunks)

        compressed_file_bits = ''.join(compressed_chunks)
        end_time_processing = time.time()
        compressed_bytes = math.ceil(len(compressed_file_bits) / 8)

        file_processing_seconds = round(end_time_processing - start_file_processing, 2)
        file_processing_minutes = round((file_processing_seconds) / 60, 2)

        file_processing_time = f'{file_processing_seconds} seconds'
        if file_processing_minutes > 8:
            file_processing_time = f'{file_processing_minutes} minutes'

        print(f'Compression params: chunk={chunk_size} bytes, {window_size=} bytes, decapitalization={decapitalize}')
        print(f'It took {file_processing_time} to process file {file_path}')
        print(f'Source file size {file_size_bytes} bytes. Compressed file size {compressed_bytes} bytes.')
        print(f'Compression ratio: {round(file_size_bytes / compressed_bytes, 3)}')
        print('-------------------------------')


def main():
    chunk_sizes = [65536]
    files = [
        'samples/Lorem-Ipsum.txt',
        'samples/Dialogues-David-Hume.txt',
        'samples/CharlesDickens-OliverTwist.txt'
    ]

    for file in files:
        for chunk in chunk_sizes:
            compress_file_print_stat(file, chunk_size=chunk)


if __name__ == '__main__':
    main()
