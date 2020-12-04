import sys


def print_err(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)
