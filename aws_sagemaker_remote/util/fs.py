import os


def ensure_path(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)


def write_chunks(path, chunks):
    ensure_path(path)
    if isinstance(chunks, (str, bytes)):
        chunks = [chunks]
    if isinstance(chunks[0], str):
        mode = 'w'
    elif isinstance(chunks[0], bytes):
        mode = 'wb'
    else:
        raise ValueError("Unhandled chunk type: {}".format(type(chunks[0])))
    with open(path, mode) as f:
        for chunk in chunks:
            f.write(chunk)
