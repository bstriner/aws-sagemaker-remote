import os
from pathlib import Path
from urllib.parse import urlparse, urljoin
from urllib.request import pathname2url, url2pathname
import sagemaker
from sagemaker.s3 import S3Uploader
from aws_sagemaker_remote.args import PathArgument
from aws_sagemaker_remote.util.cli_argument import cli_argument
from aws_sagemaker_remote.s3 import parse_s3, get_file_type, FileType


def process_channels(channels, args, session, prefix):
    if not channels:
        return {}
    channels = read_channel_arguments(channels, args=args)
    channels = expand_list_channels(channels)
    channels = remove_empty_channels(channels)
    channels = parse_channel_arguments(channels, session=session)
    channels = standardize_channels(channels)
    channels = upload_local_channels(channels, session=session, prefix=prefix)
    channels = expand_folder_channels(channels, session=session)
    channels = expand_repeated_channels(channels)
    return channels


def read_channel_arguments(channels, args):
    chs = {}
    for k, v in channels.items():
        chs[k] = v.copy(
            local=getattr(args, k),
            mode=getattr(args, f"{k}_mode"),
            repeat=getattr(args, f"{k}_repeat"),
            shuffle=getattr(args, f"{k}_shuffle")
        )
    return chs


def remove_empty_channels(channels):
    chs = {}
    for k, v in channels.items():
        if v.local:
            chs[k] = v
        else:
            assert v.optional
    return chs


def expand_list_channels(channels):
    chs = {}
    for k, v in channels.items():
        if isinstance(v.local, list):
            for i, x in enumerate(v.local):
                chs[f"{k}_{i}"] = v.copy(
                    local=x
                )
        else:
            chs[k] = v
    return chs


def parse_channel_arguments(channels, session):
    return {
        k: v.copy(local=cli_argument(v.local, session=session))
        for k, v in channels.items()
    }


def standardize_channels(channels):
    return {
        k: v.copy(local=standardize_channel(v.local))
        for k, v in channels.items()
    }


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


def upload_local_channels(channels, session, prefix):
    return {
        k: channel.copy(
            local=upload_local_channel(
                channel.local, session=session,
                s3_uri="{}/{}".format(prefix, k))
        )
        for k, channel in channels.items()
    }


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
            s3_uri = "{}/{}".format(s3_uri, os.path.basename(path))
        print("Uploaded [{}] ([{}]) to [{}]".format(
            channel, path, s3_uri
        ))
        return s3_uri
    else:
        print("Type {}".format(type(s3_uri)))
        raise ValueError(
            "Unknown scheme: [{}] (uri: {})".format(url.scheme, channel))


def expand_folder_channels(channels, session):
    if isinstance(session, sagemaker.Session):
        session = session.boto_session
    s3 = session.client('s3')
    chs = {}
    """
    v.mode in [
        'AugmentedManifestFolder',
        'ManifestFolder',
        'AugmentedManifestFolderWrapped',

        #todo: Wrapped?
    ]
    """
    for k, v in channels.items():
        if (
            "Folder" in v.mode
        ):
            target_mode = v.mode.replace("Folder", "File")
            uri = urlparse(v.local)
            url = parse_s3(uri, trailing=True)
            assert url
            manifests = s3.list_objects_v2(
                Bucket=url["Bucket"],
                # Delimiter='string',
                # EncodingType='url',
                # MaxKeys=123,
                Prefix=url['Key'],
                # ContinuationToken='string',
                # FetchOwner=True|False,
                # StartAfter='string',
                # RequestPayer='requester',
                # ExpectedBucketOwner='string'
            )
            if 'Contents' not in manifests:
                raise ValueError("Cannot find contents of bucket [{}] key [{}]".format(
                    url["Bucket"], url['Key']
                ))
            for i, manifest in enumerate(manifests['Contents']):
                mkey = manifest['Key'].lstrip('/')
                bn, _ = os.path.splitext(os.path.basename(mkey))
                s3_data = "s3://{}/{}".format(url["Bucket"], mkey)
                chs["{}_{}".format(k, bn.replace("-", "_"))] = v.copy(
                    local=s3_data,
                    mode=target_mode
                )
        else:
            chs[k] = v
    return chs


def expand_repeated_channels(channels):
    chs = {}
    for k, v in channels.items():
        if v.repeat > 1:
            for i in range(v.repeat):
                chs[f"{k}_repeat_{i}"] = v.copy(
                    repeat=1
                )
        else:
            chs[k] = v
    return chs


def set_suffixes(channels, session, hyperparameters):
    if isinstance(session, sagemaker.Session):
        session = session.boto_session
    s3 = session.client('s3')
    for k, v in channels.items():
        key = '{}-suffix'.format(k.replace('_', '-'))
        if v.mode in ['File']:
            fileType = get_file_type(v.local, s3=s3)
            if fileType == FileType.FILE:
                hyperparameters[key] = os.path.basename(v.local)
            elif fileType == FileType.FOLDER:
                if key in hyperparameters:
                    del hyperparameters[key]
            else:
                raise ValueError()
        else:
            if key in hyperparameters:
                del hyperparameters[key]
