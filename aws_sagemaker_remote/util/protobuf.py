import struct
import numpy as np
from sagemaker.amazon.record_pb2 import Record
from sagemaker.amazon.common import _write_recordio
import json
import io
from aws_sagemaker_remote.util.logging_util import print_err

try:
    from mlio.integ.numpy import to_numpy
except:
    print_err(
        "Python `mlio` package not installed. \
        Some aws-sagemaker-remote features may not be available"
    )

LENGTH_FEATURE = "{}_length"


def decode_scalar(data):
    ar = to_numpy(data)
    assert ar.size == 1
    return ar.item()


def encode_binary(data):
    file_size = len(data)
    pad = ((4-(file_size % 4)) % 4)
    if pad > 0:
        data = data + (b"\x00"*pad)
    data = struct.unpack("i"*(len(data)//4), data)
    data = np.array(data, dtype=np.int32)
    return data


def decode_binary(data, length):
    view = memoryview(data)
    view = view[:length]
    #view = view.tobytes()
    return view


def decode_bytesio_feature(features, key):
    size = decode_scalar(features[LENGTH_FEATURE.format(key)])
    data = decode_bytesio(features[key], size)
    return data


def decode_string_feature(features, key):
    size = decode_scalar(features[LENGTH_FEATURE.format(key)])
    data = decode_string(features[key], size)
    return data


def decode_string(data, length):
    return decode_binary(data, length).tobytes().decode('utf-8')


def decode_strings(datas, lengths):
    return [
        decode_string(data, length) for data, length in zip(datas, lengths)
    ]


def decode_bytesio(data, length):
    return io.BytesIO(decode_binary(data, length))


def write_feature_tensor(record, vector, key):
    """
    Args:
        resolved_type:
        record:
        vector:
    """
    if isinstance(vector, str):
        vector = vector.encode('utf-8')

    if isinstance(vector, bytes):
        record.features[key].int32_tensor.values.extend(
            encode_binary(vector)
        )
        record.features[LENGTH_FEATURE.format(key)].int32_tensor.values.extend(
            [len(vector)]
        )
    elif vector.dtype == np.int32:
        record.features[key].int32_tensor.values.extend(vector)
    elif vector.dtype == np.float64:
        record.features[key].float64_tensor.values.extend(vector)
    elif vector.dtype == np.float32:
        record.features[key].float32_tensor.values.extend(vector)
    else:
        raise ValueError("Unhandled type {}".format(vector.dtype))


def write_record(file, features=None, metadata=None):
    record = Record()
    record.Clear()
    """
    print(record)
    print(dir(record))
    print(record.features)
    print("data: {}, {}".format(type(data), len(data)))
    print(dir(record.features["values"].bytes.value))
    """
    if features:
        for k, v in features.items():
            write_feature_tensor(
                record,
                v,
                k
            )
    if metadata:
        if not isinstance(metadata, str):
            metadata = json.dumps(metadata)
        record.metadata = metadata
    # print(record.metadata)
    # print(dir(record.metadata))
    # record.metadata.val
    _write_recordio(
        file, record.SerializeToString()
    )


if __name__ == '__main__':
    s = "hello world"
    l = len(s)
    b = s.encode('utf-8')
    e = encode_binary(b)
    o = decode_binary(e, l).tobytes()
    r = o.decode('utf-8')
    print(r)
