import os
from pathlib import Path
from urllib.parse import urlparse, urljoin
from urllib.request import pathname2url, url2pathname
from sagemaker.s3 import S3Uploader


def standardize_channel(channel):
    if os.path.exists(channel):
        return Path(os.path.abspath(channel)).as_uri()
    else:
        url = urlparse(channel)
        if url.scheme == 's3':
            return channel
        elif url.scheme in ['file', '']:
            path = url2pathname(url.path)
            if os.path.exists(path):
                return Path(path).as_uri()
            else:
                raise FileNotFoundError(
                    "Channel input [{}] does not exist".format(channel))


def standardize_channels(channels):
    return {k: standardize_channel(v) for k, v in channels.items()}


def upload_local_channel(channel, session, s3_uri):
    url = urlparse(channel)
    if url.scheme == 's3':
        return channel
    elif url.scheme == 'file':
        path = url2pathname(url.path)
        S3Uploader.upload(
            local_path=path,
            desired_s3_uri=s3_uri,
            sagemaker_session=session
        )
        if os.path.isfile(path):
            #todo: urljoin
            s3_uri =  "{}/{}".format(s3_uri, os.path.basename(path))
        print("Uploaded [{}] ([{}]) to [{}]".format(
            channel, path, s3_uri
        ))
        return s3_uri
    else:
        raise ValueError("Unknown scheme: [{}]".format(url.scheme))


def upload_local_channels(channels, session, prefix):
    return {
        k: upload_local_channel(channel, session=session,
                                s3_uri="{}/{}".format(prefix, k))
        for k, channel in channels.items()
    }

