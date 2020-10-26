import sys


def chunk_iterable(it, size, last='skip'):
    assert last in ['skip', 'yield', 'error']
    i = iter(it)
    ret = []
    try:
        if last in ['yield', 'error']:
            while True:
                ret = []
                for _ in range(size):
                    ret.append(next(i))
                yield ret
        else:
            while True:
                yield [next(i) for _ in range(size)]
    except StopIteration:
        if last == 'yield':
            yield ret
        elif last == 'error':
            if len(ret):
                raise ValueError(
                    "Incomplete final chunk in chunk_iterable (len: {})".format(len(ret)))
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
