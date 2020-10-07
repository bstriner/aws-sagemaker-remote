import sagemaker
import os
import click
import re
from sagemaker.s3 import S3Uploader
import tarfile
from sagemaker.utils import _tmpdir
import boto3
from urllib.parse import urlparse


def upload(src, dst, gz, session: sagemaker.Session):
    if not os.path.exists(src):
        raise click.UsageError("Source must exist")
    if not dst.startswith('s3://'):
        if dst.startswith('/'):
            dst = dst[1:]
        bucket = session.default_bucket()
        dst = 's3://{}/{}'.format(bucket, dst)
    url = urlparse(dst)
    assert url.scheme == 's3'
    bucket = url.netloc
    key = url.path
    if key.startswith('/'):
        key = key[1:]
    if os.path.isfile(src):
        if gz:
            raise click.UsageError(
                "Option gz is only valid for source directories")
        s3 = session.boto_session.client('s3')
        s3.upload_file(src, bucket, key)
    elif os.path.isdir(src):
        if gz:
            if not re.match(".*\\.(tar\\.gz||tgz)$", dst, re.IGNORECASE):
                raise click.UsageError(
                    "Destination should end in .tar.gz or tgz")
            s3_dst = os.path.dirname(dst)
            file_name = os.path.basename(dst)
            with _tmpdir() as tmp:
                p = os.path.join(tmp, file_name)
                with tarfile.open(p, 'w:gz') as arc:
                    arc.add(name=src, arcname='.', recursive=True)
                s3 = session.boto_session.client('s3')
                s3.upload_file(p, bucket, key)
        else:
            S3Uploader.upload(
                local_path=src,
                desired_s3_uri=dst,
                sagemaker_session=session
            )
    else:
        raise click.UsageError("Source must be file or directory")
