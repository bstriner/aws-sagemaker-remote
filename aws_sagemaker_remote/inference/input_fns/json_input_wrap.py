import os
import json
import mimetypes
import boto3

from aws_sagemaker_remote.inference.mime import JSON_TYPES, MIME_KEYS
from aws_sagemaker_remote.s3 import get_file_bytes


def get_mime(info, uri):
    mime = None
    for k in MIME_KEYS:
        if k in info and info[k]:
            mime = info[k]
    if not mime:
        mime, _ = mimetypes.guess_type(uri)
    return mime


def get_extension(info, uri):
    if 'extension' in info:
        extension = info['extension']
    else:
        _, extension = os.path.splitext(uri)
    if extension.startswith("."):
        extension = extension[1:]
    return extension


def json_input_wrap(request_body, request_content_type, profile_name=None):
    if request_content_type in JSON_TYPES:
        if isinstance(request_body, bytes):
            request_body = request_body.decode('utf-8')
        info = json.loads(request_body)
        info = {
            k.lower(): v for k, v in info.items()
        }
        if 's3' in info:
            uri = info['s3']
            uri = uri.strip()
            #print("S3 Json: `{}`".format(uri))
            #url = parse_s3(uri)
            session = boto3.Session(profile_name=profile_name)
            s3 = session.client('s3')
            data = get_file_bytes(uri, s3=s3)
            extension = get_extension(info=info, uri=uri)
            mime = get_mime(info=info, uri=uri)
            #print(f"get_mime `{mime}` `{info}` `{uri}`")
            return data, extension, mime
        elif 'local' in info:
            path = info['local']
            if not os.path.exists(path):
                raise FileNotFoundError("File [{}] not found".format(path))
            with open(path, 'rb') as f:
                data = f.read()
            extension = get_extension(info=info, uri=path)
            mime = get_mime(info=info, uri=path)
            #assert isinstance(mime, str)
            return data, extension, mime
        else:
            raise ValueError(
                'JSON requests should include an `s3` or `local` key')
    else:
        extension = mimetypes.guess_extension(request_content_type)
        if not extension:
            print(f"Unknown extension for mime `{request_content_type}`")
        if extension and extension.startswith("."):
            extension = extension[1:]
        return request_body, extension, request_content_type


if __name__ == '__main__':
    request_body, extension, request_content_type = json_input_wrap(
        "{\"s3\":\"s3://voicebucket102512-dev/uploads/0ff0c8df-fc97-4117-a4f1-c2183f062cfe/0bcd0881-ce88-4ec6-b1f4-cf1897deb577.weba\"}",
        "application/json",
        profile_name='rita'
    )
    print("{}, {}, {}".format(
        len(request_body),
        extension,
        request_content_type
    ))
    print(get_mime({},'s3://asdasd/asasd.weba'))
    print(get_mime({},'s3://asdasd/asasd.mp3'))
    print(get_mime({},'s3://asdasd/asasd.mpeg'))
     