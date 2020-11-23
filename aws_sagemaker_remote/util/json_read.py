import json
from aws_sagemaker_remote.util.fields import get_field
from aws_sagemaker_remote.util.processing import processing_json
import os
from urllib.parse import urlparse


def json_read(path, field):
    with open(path, 'r') as f:
        data = json.load(f)
    data = processing_json(data)
    return get_field(data, field)


def urlparse_safe(url):
    try:
        return urlparse(url)
    except Exception:
        return None


def json_urlparse(url):
    if(url):
        uri = urlparse_safe(url)
        if uri and uri.scheme == 'json':
            path = [uri.netloc, uri.path]
            path = [p for p in path if p]
            path = "".join(path)
            if not uri.fragment:
                raise ValueError(
                    "URL fragment required for JSON inputs [{}]".format(url))
            url = json_read(path, uri.fragment)
            print("Read value [{}] from [{}]: [{}]".format(
                uri.fragment, path, url))
    return url


def json_converter(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()  # __str__()
    else:
        raise ValueError("unknown: {}".format(o))


if __name__ == '__main__':
    print(json_urlparse('json://output/dataprep.json#ProcessingOutputConfig.Outputs.output.S3Output.S3Uri'))
