
import numpy
from io import BytesIO
import torch
from scipy.io import wavfile
import json
from urllib.parse import urlparse
import boto3
import os

def input_fn(request_body, request_content_type):
    request_content_type = (request_content_type or "").strip()
    if request_content_type in ['audio/wav', 'audio/wave', 'audio/x-wav']:
        fs, data = wavfile.read(BytesIO(request_body))
        #data = torch.from_numpy(data)
        return fs, data
    elif request_content_type in ['application/json','text/javascript','application/javascript','text/json']:
        if isinstance(request_body, bytes):
            request_body = request_body.decode('utf-8')
        info = json.loads(request_body)
        if 's3' in info:
            uri = info['s3']
            url = urlparse(uri)
            bucket = url.netloc
            ext = os.path.splitext(uri)[-1]
            ext = ext.lstrip(".")
            key = url.path.lstrip("/")
            session = boto3.Session()
            s3 = session.client('s3')
            obj = s3.get_object(Bucket=bucket, Key=key)
            contents = BytesIO(obj['Body'].read())
            if ext.lower() == 'wav':
                fs, data = wavfile.read(contents)
                return fs, data
            else:
                raise ValueError("s3 object [{}] unknown extension [{}]".format(uri, ext))
        elif 'local' in info:
            path = info['local']
            if not os.path.exists(path):
                raise FileNotFoundError("File [{}] not found".format(path))
            fs, data = wavfile.read(path)
            return fs, data
        else:
            raise ValueError('JSON requests should include an `s3` or `local` key')  
    else:
        raise ValueError(
            "Unsupported content type: \"{}\"".format(request_content_type))
