from glob import glob
import os
import shutil


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


def copy_contents(src, dst, ignore=None):
    os.makedirs(dst, exist_ok=True)
    for root, dirs, files in os.walk(src):
        if ignore:
            dirs = [d for d in dirs if d not in ignore(root, dirs)]
            files = [f for f in files if f not in ignore(root, files)]
        for d in dirs:
            path = os.path.join(root, d)
            dpath = os.path.join(dst, path[len(src)+1:])
            if os.path.exists(dpath):
                shutil.rmtree(dpath)
            shutil.copytree(path, dpath)
        for f in files:
            path = os.path.join(root, f)
            dpath = os.path.join(dst, path[len(src)+1:])
            if os.path.exists(dpath):
                os.remove(dpath)
            shutil.copyfile(path, dpath)
