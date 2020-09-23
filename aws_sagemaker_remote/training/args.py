import argparse
from distutils.util import strtobool
import os
from ..args import variable_to_argparse, bool_argument, sagemaker_profile_args, PROFILE
from .config import SageMakerTrainingConfig

CHANNEL_HELP = """Input channel [{channel}].
Set to local path and it will be uploaded to S3 and downloaded to SageMaker.
Set to S3 path and it will be downloaded to SageMaker.
(default: [{default}])
"""
TRAINING_IMAGE = '683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo-sagemaker-training:latest'
TRAINING_INSTANCE = 'ml.m5.large'
TRAINING_ROLE = 'aws-sagemaker-remote-training-role'
BASE_JOB_NAME = 'training-job'


def sagemaker_training_args(
    parser: argparse.ArgumentParser,
    script,
    source='',
    base_job_name=BASE_JOB_NAME,
    job_name='',
    profile=PROFILE,
    run=False,
    wait=True,
    inputs=None,
    dependencies=None,
    additional_arguments=None,
    argparse_callback=None,
    model_dir='output/model',
    output_dir='output/output',
    training_image=TRAINING_IMAGE,
    training_instance=TRAINING_INSTANCE,
    training_role=TRAINING_ROLE,
    enable_sagemaker=True,
    experiment_name=None,
    trial_name=None
):
    r"""
    Configure ``argparse.ArgumentParser`` for training scripts.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        Parser to configure
    script : str
        Path to script file to execute.
        Set default for ``--sagemaker-script``
    source : str, optional
        Path of source directory to upload.
        Must include ``script`` path.
        Defaults to directory containing ``script`` if not provided.
    base_job_name : str, optional
        Job name will be generated from ``base_job_name`` and a timestamp if ``job_name`` is not provided.
        Set default for ``--sagemaker-base-job-name``.
    job_name : str, optional
        Job name is used for tracking and organization. 
        Generated from ``base_job_name`` if not provided.
        Use ``base_job_name`` and leave ``job_name`` blank for most use-cases.
        Set default for ``--sagemaker-job-name``.
    profile : str, optional
        AWS profile to use for session. 
        Set default for ``--sagemaker-profile``.
    run : bool, optional
        Run on SageMaker. 
        Set default for ``--sagemaker-run``.
    wait : bool, optional
        Wait for SageMaker processing to complete. 
        Set default for ``--sagemaker-wait``.
    inputs : dict(str,str), optional
        Dictionary of input arguments.
        For eack key and value, create an argument ``--key`` that defaults to value.
        * Running locally, input arguments are unmodified.
        * Running remotely, inputs are set to appropriate SageMaker mount points. Local inputs are uploaded automatically.
    dependencies : dict(str, str)
        Dictionary of modules.
        For eack key and value, create an argument ``--module-key`` that defaults to value. 
        This controls the path of a dependency of your code.
        The files at the given path will be uploaded to S3, downloaded to SageMaker, and put on PYTHONPATH.    
    additional_arguments: list, optional
        List of tuple of positional args and keyword args for ``argparse.ArgumentParser.add_argument``.
        Use to add additional arguments to the script.
    argparse_callback: function, optional
        Function accepting one argument ``parser:argparse.ArgumentParser`` that adds additional arguments.
        Use to add additional arguments to the script.
    model_dir: string, optional
        Directory to save trained model.
        Set default for ``--model-dir``.
    output_dir: string, optional
        Directory to save outputs (images, logs, etc.).
        Set default for ``--output-dir``.
    training_image : str, optional
        URI of ECR or DockerHub Docker image to use for training. 
        Set default for ``--sagemaker-training-image``.
    training_instance : str, optional
        Type of instance to use for training (e.g., ``ml.t3.medium``). 
        Set default for ``--sagemaker-training-instance``.
    training_role : str, optional
        AWS IAM role name to use for training. Will be created if it does not exist. 
        Set default for ``--sagemaker-training-role``.
    experiment_name : str, optional
        Name of experiment. Required if ``trial_name`` is provided.
        Set default for ``--sagemaker-experiment-name``.
    trial_name : str, optional
        Name of trial within experiment. 
        Set default for ``--sagemaker-trial-name``.
    enable_sagemaker : bool, optional
        * True: Include SageMaker command-line options.
        * False: Only include local command-line options
    """
    if enable_sagemaker:
        sagemaker_profile_args(parser=parser, profile=profile)
        bool_argument(parser, '--sagemaker-run', default=run,
                    help="Run training on SageMaker (yes/no default={})".format(run))
        bool_argument(parser, '--sagemaker-wait', default=run,
                    help="Wait for SageMaker training to complete and tail logs files (yes/no default={})".format(wait))
        parser.add_argument(
            '--sagemaker-script',
            default=script,
            help='Script to run on SageMaker. (default: [{}])'.format(script))
        parser.add_argument(
            '--sagemaker-source',
            default=source,
            help='Source to upload to SageMaker. '
            'Must contain script. '
            'If blank, default to directory containing script. '
            '(default: [{}])'.format(source))
        parser.add_argument(
            '--sagemaker-training-instance',
            default=training_instance,
            help='Instance type for training')
        parser.add_argument(
            '--sagemaker-training-image',
            default=training_image,
            help='Docker image for training')
        parser.add_argument(
            '--sagemaker-training-role',
            default=training_role,
            help='Docker image for training')
        parser.add_argument(
            '--sagemaker-base-job-name',
            default=base_job_name,
            help='Base job name for tracking and organization on S3.'
            ' A job name will be generated from the base job name unless a job name is specified.')
        parser.add_argument(
            '--sagemaker-job-name',
            default=job_name,
            help='Job name for tracking. Use --base-job-name instead and a job name will be automatically generated with a timestamp.')
        parser.add_argument(
            '--sagemaker-experiment-name',
            default=experiment_name,
            help='Name of experiment in SageMaker tracking.')
        parser.add_argument(
            '--sagemaker-trial-name',
            default=trial_name,
            help='Name of experiment trial in SageMaker tracking.')
        sagemaker_training_dependency_args(
            parser=parser, dependencies=dependencies)
    sagemaker_training_model_args(parser=parser, model_dir=model_dir)
    sagemaker_training_output_args(parser=parser, output_dir=output_dir)
    sagemaker_training_channel_args(parser=parser, inputs=inputs)
    if additional_arguments:
        for args, kwargs in additional_arguments:
            parser.add_argument(*args, **kwargs)
    if argparse_callback:
        argparse_callback(parser)
    return SageMakerTrainingConfig(inputs=inputs, dependencies=dependencies)


def sagemaker_training_output_args(parser: argparse.ArgumentParser, output_dir):
    output_dir = os.environ.get('SM_OUTPUT_DIR', output_dir)
    parser.add_argument('--output-dir', type=str,
                        default=output_dir,
                        help='directory for checkpoints, logs, images, or other output files (default: "{}")'.format(output_dir))


def sagemaker_training_dependency_args(parser: argparse.ArgumentParser, dependencies):
    if dependencies:
        for k, v in dependencies.items():
            flag = variable_to_argparse(k)
            parser.add_argument(flag, type=str,
                                default=k,
                                help='Directory for dependency [{}] (default: "{}")'.format(k, v))


def sagemaker_training_channel_args(parser: argparse.ArgumentParser, inputs):
    if inputs:
        for channel, default in inputs.items():
            flag = variable_to_argparse(channel)
            env_key = 'SM_CHANNEL_{}'.format(channel.upper())
            if env_key in os.environ:
                default = os.environ[env_key]
            parser.add_argument(
                flag, type=str,  default=default,
                help=CHANNEL_HELP.format(channel=channel, default=default))


def sagemaker_training_model_args(parser: argparse.ArgumentParser,
                                  model_dir='model'
                                  ):
    # Overwrite default if running on SageMaker
    model_dir = os.environ.get('SM_MODEL_DIR', model_dir)
    parser.add_argument(
        '--model-dir', type=str,
        default=model_dir,
        help='Directory to save final model (default: {})'.format(model_dir))


def sagemaker_training_parser_for_docs():
    parser = argparse.ArgumentParser()
    script = 'script.py'
    sagemaker_training_args(
        parser=parser, script=script,
        inputs={
            'input': 'path/to/input'
        },
        dependencies={
            'my_module': 'path/to/my_module'
        })
    return parser
