
import argparse
from aws_sagemaker_remote.lamb.js.lamb import ensure_lambda_js
from aws_sagemaker_remote.batch.job import create_job
import boto3
from aws_sagemaker_remote.args import bool_argument
from aws_sagemaker_remote.lamb.lamb import update_function
from aws_sagemaker_remote.util.cloudformation import get_cloudformation_output

# todo: command wrapping
from aws_sagemaker_remote.commands import Command


class BatchConfig(object):
    def __init__(
        self,
        stack_name,
        code_dir,
        profile='default',
        description='Batch Processing',
        # role_name='aws-sagemaker-remote-batch-role',
        argparse_callback=None,
        env_callback=None,
        webpack=True,
        manifest=None,
        report="sagemaker://aws-sagemaker-remote/batch-reports"
    ):
        self.stack_name = stack_name
        self.code_dir = code_dir
        self.profile = profile
        self.argparse_callback = argparse_callback
        self.env_callback = env_callback
        self.webpack = webpack
        self.manifest = manifest
        self.report = report
        # self.role_name=role_name
        self.description = description


class BatchCommand(Command):
    def __init__(self, config: BatchConfig, help=None):
        self.config = config
        super(BatchCommand, self).__init__(help=help)

    def configure(self, parser: argparse.ArgumentParser):
        batch_argparse_callback(
            parser,
            config=self.config
        )

    def run(self, args):
        batch_run(args, self.config)


def batch_argparse_callback(
    parser: argparse.ArgumentParser,
    config: BatchConfig
):
    parser.add_argument(
        '--profile', type=str, default=config.profile, help='AWS profile name'
    )
    parser.add_argument(
        '--stack-name',
        type=str,
        default=config.stack_name,
        help='Stack name for deploying Lambda',
        required=not config.stack_name
    )
    parser.add_argument(
        '--code-dir',
        type=str,
        default=config.code_dir,
        help='Directory of Lambda code',
        required=not config.code_dir
    )
    bool_argument(
        parser, '--deploy',
        default=False,
        help='Force Lambda deployment even if function already exists'
    )
    bool_argument(
        parser,
        '--confirmation-required',
        default=True,
        help='Require confirmation in console to run job'
    )
    parser.add_argument(
        '--manifest',
        type=str,
        default=config.manifest,
        help='File manifest to process',
        required=not config.manifest
    )
    parser.add_argument(
        '--report',
        type=str,
        default=config.report,
        help='S3 path to store report'
    )
    parser.add_argument(
        '--description',
        type=str,
        default=config.description,
        help='S3 path to store report'
    )
    # parser.add_argument(
    #    '--role-name', type=str, default=config.role_name, help='S3 path to store report'
    # )
    if config.argparse_callback:
        config.argparse_callback(parser)


def batch_run(args, config: BatchConfig):
    session = boto3.Session(profile_name=args.profile)
    sts = session.client('sts')
    s3control = session.client('s3control')
    s3 = session.client('s3')
    lambda_client = session.client('lambda')
    cloudformation = session.client('cloudformation')

    # Create function
    ensure_lambda_js(
        path=args.code_dir,
        stack_name=args.stack_name,
        session=session,
        webpack=config.webpack,
        deploy=args.deploy
    )
    function_arn, batch_role_arn = get_cloudformation_output(
        cloudformation=cloudformation,
        stack_name=args.stack_name,
        output_key=[
            'LambdaFunctionArn',
            'BatchRoleArn'
        ]
    )
    assert function_arn
    assert batch_role_arn

    # Versioned function for this call
    lambda_env = {}
    if config.env_callback:
        lambda_env.update(config.env_callback(args))
    function_arn = update_function(
        lambda_client=lambda_client,
        function_name=function_arn,
        env=lambda_env
    )

    #manifest = args.manifest
    #report = args.report
    # todo: report prefix /

    identity = sts.get_caller_identity()
    account_id = identity['Account']
    print("AccountID: {}".format(account_id))

    create_job(
        session=session,
        manifest=args.manifest,
        report=args.report,
        arn=function_arn,
        account_id=account_id,
        description=args.description,
        role_name=batch_role_arn,  # args.role_name,
        confirmation_required=args.confirmation_required
    )
