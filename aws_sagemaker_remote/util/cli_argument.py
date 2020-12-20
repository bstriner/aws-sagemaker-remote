import json
import os
from urllib.parse import urlparse
import datetime
import sagemaker
import boto3
import csv
from aws_sagemaker_remote.util.fields import get_field
from aws_sagemaker_remote.util.processing import processing_describe
from aws_sagemaker_remote.util.batch import batch_describe
from aws_sagemaker_remote.util.training import training_describe
from aws_sagemaker_remote.util.json_read import json_read


def cli_argument_stack(urls, session=None):
    #print("stack: {}".format(urls))
    if isinstance(session, boto3.Session):
        session = sagemaker.Session(boto_session=session)
    cur = None
    for i, url in enumerate(urls):
        if i == 0:
            cur = url
        else:
            op = url.split(":")
            if op[0] == "json":
                if len(op) != 2:
                    raise ValueError("json requires 1 argument")
                cur = json_read(cur, op[1], session=session)
            elif op[0] == 'sagemaker':
                if len(op) != 1:
                    raise ValueError("sagemaker requires 0 arguments")
                if cur.startswith("/"):
                    cur = cur[1:]
                bucket = session.default_bucket()
                cur = f"s3://{bucket}/{cur}"
            elif op[0] == 'processing':
                if len(op) != 2:
                    raise ValueError("processing requires 1 argument")
                cur = processing_describe(
                    job_name=cur,
                    session=session,
                    field=op[1]
                )
            elif op[0] == 'training':
                if len(op) != 2:
                    raise ValueError("training requires 1 argument")
                cur = training_describe(
                    job_name=cur,
                    session=session,
                    field=op[1]
                )
            elif op[0] == 'batch':
                if len(op) != 2:
                    raise ValueError("batch requires 1 argument")
                cur = batch_describe(
                    job_id=cur,
                    session=session,
                    field=op[1]
                )
                # if op[1] not in ['failure', 'success']:
                #    raise ValueError(
                #        "batch op argument must be `failure` or `success`")
            else:
                print(f"Unknown op {op[0]}")
    return cur


def cli_argument(url, session=None):
    if(url):
        vals = next(csv.reader([url]))
        return cli_argument_stack(vals, session=session)
    return None


if __name__ == '__main__':
    session = boto3.Session(profile_name='default')
    print(cli_argument(
        'output/batch.json,json:JobId,batch:Report.s3,json:Results.failed.s3',
        session=session
    ))
    print(cli_argument(
        'output/batch.json,json:JobId,batch:Report.s3,json:Results.succeeded.s3',
        session=session
    ))
    # print(cli_argument(
    #    'output/batch.json,json:JobId,batch:failed',
    #    session=session
    # ))
"""
    print(cli_argument(
        'output/dataprep.json,sagemaker'
    ))
    print(cli_argument(
        'output/dataprep.json,json:ProcessingOutputConfig.Outputs.output.S3Output.S3Uri'
    ))
    """
