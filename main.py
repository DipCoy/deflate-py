import logging

from deflate.utils import read_file_by_chunks

logging.basicConfig(level=logging.DEBUG)

from deflate.encoder import DeflateLikeEncoder


def main():
    WINDOW_SIZE = 32768
    CHUNK_SIZE = 1024

    encoder = DeflateLikeEncoder(WINDOW_SIZE)

    total_chunks = 0

    for chunk in read_file_by_chunks('samples/CharlesDickens-OliverTwist.txt', CHUNK_SIZE):
        encoder.encode(chunk)
        total_chunks += 1
        print(total_chunks)


if __name__ == '__main__':
    main()
