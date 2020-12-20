import os
import shutil
import re

def python_ignore(path, names):
    return [
        name for name in names
        if re.match("__pycache__|\\.git", name)
    ]


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

def copy_file_or_dir(src, dst, file_subfolder=False):
    if os.path.exists(dst):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        else:
            os.remove(dst)
    if os.path.isdir(src):
        shutil.copytree(
            src,
            dst,
            # dirs_exist_ok=True,
            ignore=python_ignore
        )
        return dst
    else:
        if file_subfolder:
            os.makedirs(dst, exist_ok=True)
            dst = os.path.join(
                    dst,
                    os.path.basename(dst)
                )
            shutil.copyfile(
                src,
                dst
            )
            return dst
        else:
            shutil.copyfile(
                src,
                dst
            )
            return dst
