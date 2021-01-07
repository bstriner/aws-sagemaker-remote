import sys
import json
from sagemaker.amazon.common import read_recordio
import io
import array
from itertools import count
import multiprocessing
import warnings
from aws_sagemaker_remote.util.logging_util import print_err
try:
    import mlio
    from mlio.integ.torch import as_torch
except:
    print_err(
        "Python `mlio` package not installed. \
        Some aws-sagemaker-remote features may not be available"
    )

MAGIC = 0xCED7230A


def epoch_iterable(epochs):
    if epochs == 0:
        return count()
    else:
        return range(epochs)


class ProtobufPipeIterator(object):
    def __init__(self, path, features, count=0, epochs=1, **reader_params):
        print(f"Created ProtobufPipeIterator path: {path}, count: {count}")
        self.path = path
        self.features = features
        self.reader_params = reader_params
        #self.count = count
        # self.pipe = mlio.SageMakerPipe(self.path) #fifo_id =
        self.epochs = epochs
        self.count = multiprocessing.Value('i', count)
        #self.lock = multiprocessing.Lock()

    def iterate_features(self, examples):
        for example in examples:
            yield {
                k: as_torch(example[k]) for k in self.features
            }

    def increment(self):
        #with self.lock:
        fifo_id = self.count.value
        self.count.value = fifo_id+1
        return fifo_id

    def pipe_iterator(self, fifo_id=0):
        fifo_id = self.increment()
        print(f"opening pipe iterator {self.path}:{fifo_id}")
        pipe = mlio.SageMakerPipe(self.path, fifo_id=fifo_id)
        reader_params = mlio.DataReaderParams(
            dataset=[pipe],
            **self.reader_params
        )
        reader = mlio.RecordIOProtobufReader(reader_params)
        return reader

    def __iter__(self):
        iterator = self.pipe_iterator()
        epochs = epoch_iterable(self.epochs)
        for epoch in epochs:
            print(f"starting pipeiterator {self.path} {epoch}: {self.count.value}")
            if epoch > 0:
                fifo_id = self.increment()
                print(f"fifo_id {fifo_id}")
            for rec in self.iterate_features(iterator):
                yield rec
            iterator.reset()
            #print("Iterator complete")


def decode_strings_numpy(data, data_length):
    assert data.shape[0] == data_length.shape[0]
    for d, dl in zip(data, data_length):
        b = d.tobytes()
        b = b[:dl.item()]
        b = b.decode('utf-8')
        yield b


def decode_strings_torch(data, data_length):
    assert data.size(0) == data_length.size(0)
    data_np = data.numpy()
    for d, dl in zip(data_np, data_length):
        b = d.tobytes()
        b = b[:dl.item()]
        b = b.decode('utf-8')
        yield b


class RawPipeIterator(object):
    def __init__(self, path, size=1, count=0, epochs=1):
        self.path = path
        self.size = size
        #self.count = count
        # self.pipe = mlio.SageMakerPipe(self.path) #fifo_id =
        self.epochs = epochs
        self.count = multiprocessing.Value('i', count)
        self.lock = multiprocessing.Lock()

    def pipe_iterator(self):
        with self.lock:
            fifo_id = self.count.value
            self.count.value = fifo_id+1
        pipe = mlio.SageMakerPipe(self.path, fifo_id=fifo_id)
        return chunk_iterable(
            read_examples(pipe),
            self.size,
            last='error'
        )

    def __iter__(self):
        # pipe = mlio.SageMakerPipe(self.path)  # fifo_id =
        if self.epochs == 0:
            epochs = count()
        else:
            epochs = range(self.epochs)
        for epoch in epochs:
            for rec in self.pipe_iterator():
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


def read_bytes(s, cnt):
    bufs = []
    tot = 0
    while tot < cnt:
        rem = cnt-tot
        buf = bytearray(rem)
        read = s.read(buf)
        if read == 0:
            raise ValueError(
                "read 0 bytes. need {}/{} got {}".format(rem, cnt, read))
        elif read == rem:
            bufs.append(buf)
        else:
            #print("Incomplete read. wanted {}/{} got {}".format(rem, cnt, read))
            bufs.append(buf[:read])
        tot += read
    if tot != cnt:
        raise ValueError("tot {} not = cnt {}".format(tot, cnt))
    if len(bufs) == 1:
        return bufs[0]
    else:
        return b"".join(bufs)


def read_examples(pipe):
    i = 0
    read = 0
    # buf = io.BytesIO()
    # buf_size = 128
    # buf = array.array('B', [0 for _ in range(buf_size)])
    # buf = bytearray(buf_size)
    header_buf = array.array('I', [0, 0])
    s = pipe.open_read()
    print("Opened pipe")
    while True:
        read = s.read(header_buf)
        print("header {}, {}: {}: {}".format(
            i, read, header_buf, [hex(x) for x in header_buf]))
        if read == 0:
            print("Read 0 bytes. EndOfPipe.")
            break
        if read != 8:
            raise ValueError("Expected 8 got {}: {}".format(read, header_buf))
        if header_buf[0] != MAGIC:
            raise ValueError("Expected magic {} got {}".format(
                hex(MAGIC),
                hex(header_buf[0])
            ))
        length = header_buf[1]
        """
        if(length > 1024*1024*10):
            print("Length {} is too large".format(length))
            length = 601646
            data_buf = bytearray(1024)
            read = s.read(data_buf)
            print("read {}: {}".format(read, [hex(x) for x in data_buf]))
            raise ValueError()
        """
        padding = (((length+3) >> 2) << 2) - length
        data_buf = read_bytes(s, length)
        #data_buf = bytearray(length)
        #read = s.read(data_buf)
        # if read != length:
        #    raise ValueError("Expected to read {} got {}".format(length, read))
        # use data
        print("Yielding data")
        yield io.BytesIO(data_buf)
        # print("Read {} bytes".format(length))
        if padding > 0:
            read = s.read(bytearray(padding))
            if read != padding:
                raise ValueError(
                    "Expected to read padding {} but got {}".format(padding, read))

        # print("{}: {}: {}: {}".format(i, read, buf[:read], [hex(x) for x in buf[:read]]))
        i += 1
        if i > 10000:
            raise ValueError("Stuck in loop?")
        # if i > 100:
        #    break


if __name__ == '__main__':
    it = range(100)
    print(list(chunk_iterable(it, 7, last='skip')))
    print(list(chunk_iterable(it, 7, last='yield')))
    print(list(chunk_iterable(it, 10, last='error')))
    try:
        print(list(chunk_iterable(it, 7, last='error')))
    except ValueError as e:
        print(e)
