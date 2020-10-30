import sys
import json
from sagemaker.amazon.common import read_recordio


class PipeIterator(object):
    def __init__(self, path, size=1, count=0):
        self.path = path
        self.size = size
        self.count = count

    def __iter__(self):
        while True:
            with open("{}_{}".format(self.path, self.count), 'rb') as f:
                self.count += 1
                for rec in chunk_iterable(read_recordio(f), self.size, last='error'):
                    yield rec


def pipe_iterator(path, size=1):
    count = 0
    while True:
        with open("{}_{}".format(path, count), 'rb') as f:
            for rec in chunk_iterable(read_recordio(f), size, last='error'):
                yield rec
        count += 1


def read_jsonlines(path):
    with open(path) as f:
        for l in f:
            l = l.strip()
            if l:
                yield json.loads(l)


def chunk_iterable(it, size, last='skip'):
    assert last in ['skip', 'yield', 'error']
    i = iter(it)
    ret = []
    try:
        if last in ['yield', 'error']:
            while True:
                for _ in range(size):
                    ret.append(next(i))
                yield ret
                ret = []
        else:
            while True:
                yield [next(i) for _ in range(size)]
    except StopIteration:
        if last == 'yield':
            yield ret
        elif last == 'error':
            if len(ret):
                raise ValueError(
                    "Incomplete final chunk in chunk_iterable (len: {}, contents: {})".format(len(ret), [len(r) for r in ret]))
    finally:
        del i


if __name__ == '__main__':
    it = range(100)
    print(list(chunk_iterable(it, 7, last='skip')))
    print(list(chunk_iterable(it, 7, last='yield')))
    print(list(chunk_iterable(it, 10, last='error')))
    try:
        print(list(chunk_iterable(it, 7, last='error')))
    except ValueError as e:
        print(e)
