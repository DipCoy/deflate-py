

def read_file_by_chunks(file_path: str, chunk_size: int):
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break

            yield data
