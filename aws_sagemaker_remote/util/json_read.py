import json
from aws_sagemaker_remote.util.fields import get_field
import os
from urllib.parse import urlparse
import datetime
import sagemaker
import boto3
import csv
from .processing import processing_describe
from .batch import batch_describe
from .training import training_describe
from aws_sagemaker_remote.s3 import get_file_string, parse_s3


def json_read(path, field, session=None):
    if path and path.startswith("s3://"):
        if isinstance(session, sagemaker.Session):
            session = session.boto_session
        data = get_file_string(
            url=path,
            s3=session.client('s3')
        )
        data = json.loads(data)
    else:
        with open(path, 'r') as f:
            data = json.load(f)
    return get_field(data, field)


def urlparse_safe(url):
    try:
        return urlparse(url)
    except Exception:
        return None


def json_converter(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()  # __str__()
    else:
        raise ValueError("unknown: {}".format(o))
