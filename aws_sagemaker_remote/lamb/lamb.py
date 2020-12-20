import boto3
import tempfile
import os
import shutil
import re
from venv import EnvBuilder
import subprocess
import warnings
import time
import sys
from aws_sagemaker_remote.util.logging_util import print_err

LAMBDA_KEY = 'LambdaFunction'


def lambda_ignore_path(src, name):
    path = os.path.join(src, name)
    return re.search(r'dist-info|\.pyc$|__pycache__|([\\/])\.', path)


def lambda_ignore(src, names):
    return [
        name for name in names if lambda_ignore_path(src, name)
    ]


def update_function(
    lambda_client, function_name, env, timeout,
    memory
    #todo: memory
):
    response = lambda_client.update_function_configuration(
        FunctionName=function_name,
        # Role='string',
        # Handler='string',
        # Description='string',
        Timeout=timeout,
        MemorySize=memory,
        # VpcConfig={
        #    'SubnetIds': [
        #         'string',
        #     ],
        #     'SecurityGroupIds': [
        #         'string',
        #     ]
        # },
        Environment={
            'Variables': {k: str(v) for k, v in env.items()}
        }
        # ,
        # Runtime='nodejs'|'nodejs4.3'|'nodejs6.10'|'nodejs8.10'|'nodejs10.x'|'nodejs12.x'|'java8'|'java8.al2'|'java11'|'python2.7'|'python3.6'|'python3.7'|'python3.8'|'dotnetcore1.0'|'dotnetcore2.0'|'dotnetcore2.1'|'dotnetcore3.1'|'nodejs4.3-edge'|'go1.x'|'ruby2.5'|'ruby2.7'|'provided'|'provided.al2',
        # DeadLetterConfig={
        #     'TargetArn': 'string'
        # },
        # KMSKeyArn='string',
        # TracingConfig={
        #     'Mode': 'Active'|'PassThrough'
        # },
        # RevisionId='string',
        # Layers=[
        #     'string',
        # ],
        # FileSystemConfigs=[
        #     {
        #         'Arn': 'string',
        #         'LocalMountPath': 'string'
        #     },
        # ]
    )
    revision_id = response['RevisionId']
    response = lambda_client.publish_version(
        FunctionName=function_name,
        # CodeSha256='string',
        # Description='string',
        RevisionId=revision_id
    )
    arn = response['FunctionArn']
    return arn


if __name__ == '__main__':
    """
    C:\Projects\aws-sagemaker-remote\output\tmp\venv\Scripts\python.exe -m site --user-site

    lambda_create_python(
        'test-lambda-create',
        'demo/demo_batch/code'
    )
        """
