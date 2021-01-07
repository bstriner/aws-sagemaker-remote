import boto3
from urllib.request import urlparse
from botocore.exceptions import ClientError
import io
from contextlib import closing
import codecs

import os
import sagemaker
from aws_sagemaker_remote.util.fs import ensure_path
from sagemaker.s3 import S3Downloader


def get_file(url, s3):
    s3_url = parse_s3(url)
    obj = s3.get_object(**s3_url)
    return closing(obj['Body'])


def get_file_bytes(url, s3):
    with get_file(url=url, s3=s3) as f:
        return f.read()


def get_file_string(url, s3, encoding='utf-8'):
    return get_file_bytes(url=url, s3=s3).decode(encoding)


"""
def get_file_text(url, s3, encoding='utf-8'):
    with 
    text = io.TextIOWrapper(get_file(url=url, s3=s3), encoding=encoding)
    return text
"""


def parse_s3(url, trailing=None):
    if url:
        uri = urlparse(url)
        if uri.scheme != 's3':
            raise ValueError(f"Expected s3 url got {url}")
        bucket = uri.hostname
        key = uri.path
        if key.startswith("/"):
            key = key[1:]
        if trailing is not None:
            if key.endswith("/"):
                key = key[:-1]
            if trailing:
                key = f"{key}/"
        return {
            "Bucket": bucket,
            "Key": key
        }
    else:
        return None


class FileType(object):
    FILE = 'File'
    FOLDER = 'Folder'


def is_s3_folder(uri, s3):
    url = urlparse(uri)
    assert url.scheme == 's3'
    bucket = url.hostname
    key = url.path
    if key.startswith('/'):
        key = key[1:]
    if not key.endswith('/'):
        key += '/'
    try:
        response = s3.list_objects_v2(
            Bucket=bucket,
            # Delimiter='string',
            # EncodingType='url',
            MaxKeys=1,
            Prefix=key,
            # ContinuationToken='string',
            # FetchOwner=True|False,
            # StartAfter='string',
            # RequestPayer='requester',
            # ExpectedBucketOwner='string'
        )
        if response['KeyCount']:
            return True
        else:
            return False
    except ClientError:
        return False


def is_s3_file(uri, s3):
    url = urlparse(uri)
    assert url.scheme == 's3'
    bucket = url.hostname
    key = url.path
    if key.startswith('/'):
        key = key[1:]
    try:
        response = s3.head_object(
            Bucket=bucket,
            Key=key)
        return response
    except ClientError:
        return None


def get_file_type(uri, s3):
    if is_s3_file(uri, s3):
        return FileType.FILE
    elif is_s3_folder(uri, s3):
        return FileType.FOLDER
    else:
        raise ValueError(
            "Cannot determine if URI [{}] is file or folder. Check your permissions, your AWS profile connection, and that URI exists.".format(uri))


def download_file(Filename, s3, **kwargs):
    ensure_path(Filename)
    s3.download_file(
        Filename=Filename,
        **kwargs
    )


def download_folder(Filename, Bucket, Key, session):
    if isinstance(session, boto3.Session):
        session = sagemaker.Session(boto_session=session)
    ensure_path(Filename)
    S3Downloader.download(
        s3_uri=f"s3://{Bucket}/{Key}",
        local_path=Filename,
        sagemaker_session=session
    )


def download_file_or_folder(uri, session, dest, file_subfolder=True, skip_if_exist=True):
    if isinstance(session, sagemaker.Session):
        session = session.boto_session
    s3 = session.client('s3')
    ft = get_file_type(uri, s3=s3)
    url = parse_s3(uri)
    if ft == FileType.FILE:
        if file_subfolder:
            download_folder(
                session=session,
                Filename=dest,
                **url
            )
            return os.path.join(
                dest,
                os.path.basename(uri)
            )
        else:
            download_file(
                s3=s3,
                Filename=dest,
                **url
            )
            return dest
    elif ft == FileType.FOLDER:
        download_folder(
            session=session,
            Filename=dest,
            **url
        )
        return dest
    else:
        raise ValueError(f"Unhandled file type: {ft}")
    pass


def copy_s3(src, dst, s3):
    src = parse_s3(src, trailing=True)
    dst = parse_s3(dst, trailing=True)
    response = s3.list_objects_v2(
        Bucket=src["Bucket"],
        # Delimiter='string',
        # EncodingType='url',
        # MaxKeys=123,
        Prefix=src['Key'],
        # ContinuationToken='string',
        # FetchOwner=True|False,
        # StartAfter='string',
        # RequestPayer='requester',
        # ExpectedBucketOwner='string'
    )
    if 'Contents' in response:
        for file in response['Contents']:
            fkey = file['Key'].lstrip('/')
            assert fkey.startswith(src['Key'])
            fout = f"{dst['Key']}{fkey[len(src['Key']):]}"
            s3.copy_object(
                CopySource={
                    "Bucket": src['Bucket'],
                    "Key": file['Key']
                },
                Bucket=dst['Bucket'],
                Key=fout
            )
    else:
        print(f"No files found under {src}")


if __name__ == '__main__':
    session = boto3.Session(profile_name='default')
    s3 = session.client('s3')
    print(get_file_string(
        s3=s3,
        url='s3://sagemaker-us-east-1-683880991063/aws-sagemaker-remote/batch-reports/job-ee1e7233-2668-4320-9fff-e13613bd7622/manifest.json'
    ))
    copy_s3(
        's3://sagemaker-us-east-1-683880991063/demo-checkpoint',
        's3://sagemaker-us-east-1-683880991063/demo-checkpoint-cp',
        s3=s3
    )
    """
    aws --profile default s3 ls s3://sagemaker-us-east-1-683880991063/demo-checkpoint-cp/
    uri = 's3://sagemaker-us-east-1-683880991063/demo-training-inputs-2020-10-01-15-49-26-167/inputs/test_folder/test_file.txt'
    print(get_file_type(uri, s3))
    uri = 's3://sagemaker-us-east-1-683880991063/demo-training-inputs-2020-10-01-15-49-26-167/inputs/test_folder'
    print(get_file_type(uri, s3))
    uri = 's3://sagemaker-us-east-1-683880991063/demo-training-inputs-2020-10-01-15-49-26-167/inputs/test_folder/'
    print(get_file_type(uri, s3))
    uri = 's3://sagemaker-us-east-1-683880991063/demo-training-inputs-2020-10-01-15-49-26-167/inputs/test_fold'
    print(get_file_type(uri, s3))
    """
