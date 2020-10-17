import hashlib
try:
    from shutil import COPY_BUFSIZE
except:
    COPY_BUFSIZE = 1024*1024


def calc_md5(path):
    file_hash = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            fb = f.read(COPY_BUFSIZE)
            if not fb:
                break
            file_hash.update(fb)
    return file_hash.hexdigest()


def check_md5(path, md5=None):
    if md5:
        file_md5 = calc_md5(path)
        if file_md5 != md5:
            raise ValueError("MD5 mismatch. expected [{}], got [{}]".format(
                md5, file_md5
            ))
