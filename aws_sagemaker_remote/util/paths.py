from glob import glob
import os


def get_relative(file, base):
    if not file.startswith(base):
        raise ValueError("Expected [{}] to start with [{}]".format(
            file, base)
        )
    assert file[len(base)] in ["\\", "/"]
    return file[len(base)+1:]


def glob_relative(path, pattern):
    base = os.path.abspath(path)
    glob_path = os.path.join(base, "**", pattern)
    files = glob(glob_path, recursive=True)
    files = (os.path.abspath(file) for file in files)
    files = ((file, get_relative(file, base)) for file in files)
    return files
