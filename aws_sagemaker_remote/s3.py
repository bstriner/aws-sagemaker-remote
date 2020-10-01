import boto3
from urllib.request import urlparse
from botocore.exceptions import ClientError

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
            #Delimiter='string',
            #EncodingType='url',
            MaxKeys=1,
            Prefix=key,
            #ContinuationToken='string',
            #FetchOwner=True|False,
            #StartAfter='string',
            #RequestPayer='requester',
            #ExpectedBucketOwner='string'
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
        raise ValueError("Cannot determine if URI [{}] is file or folder. Check your permissions, your AWS profile connection, and that URI exists.".format(uri))

if __name__ == '__main__':
    session = boto3.Session()
    s3 = session.client('s3')
    uri = 's3://sagemaker-us-east-1-683880991063/demo-training-inputs-2020-10-01-15-49-26-167/inputs/test_folder/test_file.txt'
    print(get_file_type(uri, s3))
    uri = 's3://sagemaker-us-east-1-683880991063/demo-training-inputs-2020-10-01-15-49-26-167/inputs/test_folder'
    print(get_file_type(uri, s3))
    uri = 's3://sagemaker-us-east-1-683880991063/demo-training-inputs-2020-10-01-15-49-26-167/inputs/test_folder/'
    print(get_file_type(uri, s3))
    uri = 's3://sagemaker-us-east-1-683880991063/demo-training-inputs-2020-10-01-15-49-26-167/inputs/test_fold'
    print(get_file_type(uri, s3))
