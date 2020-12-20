# have to monkey patch to work with WSL as workaround for https://bugs.python.org/issue38633
import errno, shutil
orig_copyxattr = shutil._copyxattr
def patched_copyxattr(src, dst, *, follow_symlinks=True):
	try:
		orig_copyxattr(src, dst, follow_symlinks=follow_symlinks)
	except OSError as ex:
		if ex.errno != errno.EACCES: raise
shutil._copyxattr = patched_copyxattr