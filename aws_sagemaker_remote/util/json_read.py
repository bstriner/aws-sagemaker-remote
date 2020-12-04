import json
from aws_sagemaker_remote.util.fields import get_field
import os
from urllib.parse import urlparse
import datetime
import sagemaker
import boto3


def processing_json(description):
    description['ProcessingInputs'] = {
        pi['InputName']: pi
        for pi in
        description.get('ProcessingInputs', {})
    }
    description['ProcessingOutputConfig'] = description.get(
        'ProcessingOutputConfig', {})
    description['ProcessingOutputConfig']['Outputs'] = {
        po['OutputName']: po
        for po in
        description['ProcessingOutputConfig'].get('Outputs', {})
    }
    return description


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


def json_urlparse(url, session=None):
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
            return json_urlparse(url, session=session)
            # print("Read value [{}] from [{}]: [{}]".format(
            #    uri.fragment, path, url))
        elif uri and uri.scheme == 'sagemaker':
            if isinstance(session, boto3.Session):
                session = sagemaker.Session(boto_session=session)
            if not isinstance(session, sagemaker.Session):
                raise ValueError(
                    "session required for url {}. Expected session to be sagemaker.Session or boto3.Session got {}".format(url, type(session)))
            path = [uri.netloc, uri.path]
            path = [p for p in path if p]
            path = "".join(path)
            if path.startswith("/"):
                path = path[1:]
            # if session:
            return f"s3://{session.default_bucket()}/{path}"
    return url


def json_converter(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()  # __str__()
    else:
        raise ValueError("unknown: {}".format(o))


if __name__ == '__main__':
    print(json_urlparse(
        'json://output/dataprep.json#ProcessingOutputConfig.Outputs.output.S3Output.S3Uri'))
