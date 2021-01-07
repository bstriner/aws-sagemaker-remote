import argparse
from distutils.util import strtobool
import os
from ..args import variable_to_argparse, bool_argument, sagemaker_profile_args, PROFILE
from .config import SageMakerTrainingConfig
import json
import inspect
import types
from aws_sagemaker_remote.ecr.images import Images

CHANNEL_HELP = """Input channel [{channel}].
Set to local path and it will be uploaded to S3 and downloaded to SageMaker.
Set to S3 path and it will be downloaded to SageMaker.
(default: [{default}])
"""
CHANNEL_HELP_MODE = """Input channel [{channel}] mode.
(default: [{default}])
"""
TRAINING_INSTANCE = 'ml.m5.large'
TRAINING_ROLE = 'aws-sagemaker-remote-training-role'
BASE_JOB_NAME = 'training-job'
CHECKPOINT_LOCAL_PATH = '/opt/ml/checkpoints'

"""
def sagemaker_env_args(config):
    args = {}
    output_dir = os.environ.get('SM_OUTPUT_DIR', None)
    if output_dir:
        args['output_dir'] = output_dir
    model_dir = os.environ.get('SM_MODEL_DIR', None)
    if model_dir:
        args['model_dir'] = model_dir
    for channel in config.inputs.keys():
        env_key = 'SM_CHANNEL_{}'.format(channel.upper())
        channel_dir = os.environ.get(env_key, None)
        if channel_dir:
            args[channel] = channel_dir
    return args
"""


def is_sagemaker():
    return sagemaker_env_arg()


def sagemaker_env_arg():
    """
    Check for ``SM_TRAINING_ENV`` environment variable and return object if it exists
    """
    sm_env = os.getenv('SM_TRAINING_ENV', None)
    if sm_env:
        data = json.loads(sm_env)
        return data
    else:
        return None


def sagemaker_env_args(args: argparse.Namespace, config: SageMakerTrainingConfig):
    """
    Check for ``SM_TRAINING_ENV`` environment variable and use it to override arguments.
    """
    kwargs = vars(args)
    data = sagemaker_env_arg()
    if data:
        print("Detected SageMaker environment")
        ci = data.get('channel_input_dirs', None)
        if ci:
            for k in config.inputs.keys():
                v = ci.get(k, None)
                if not v:
                    v = {}
                    for ik, iv in ci.items():
                        if ik.startswith("{}_".format(k)):
                            v[ik[len(k)+1:]] = iv
                            kwargs[ik] = iv
                    v = v or None
                    kwargs[k] = v
                else:
                    suffix = kwargs.get('{}_suffix'.format(k), None)
                    if suffix and os.path.exists(v):
                        # todo: handle file pipes
                        v = os.path.join(v, suffix)
                    print("SageMaker input [{}]: [{}]".format(k, v))
                    kwargs[k] = v
        else:
            for k in config.inputs.keys():
                kwargs[k] = None
        output_dir = data.get('output_data_dir', None)
        if output_dir:
            kwargs['output_dir'] = output_dir
            print("SageMaker output_dir: [{}]".format(output_dir))
        model_dir = data.get('model_dir', None)
        if model_dir:
            kwargs['model_dir'] = model_dir
            print("SageMaker model_dir: [{}]".format(model_dir))
        job_name = data.get('job_name', None)
        if job_name:
            kwargs['sagemaker_job_name'] = job_name
            print("SageMaker job_name: [{}]".format(job_name))
        kwargs['sagemaker_run'] = False
        kwargs['is_sagemaker'] = True
    else:
        kwargs['is_sagemaker'] = False
    new_args = argparse.Namespace(
        **kwargs
    )
    #print("Original args: {}".format(args))
    #print("Updated args: {}".format(new_args))
    return new_args


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
    checkpoint_dir='output/checkpoint',
    checkpoint_s3='default',
    checkpoint_container=CHECKPOINT_LOCAL_PATH,
    checkpoint_initial=None,
    training_image=Images.TRAINING.tag,
    training_image_path=Images.TRAINING.path,
    training_image_accounts=Images.TRAINING.accounts,
    training_instance=TRAINING_INSTANCE,
    training_role=TRAINING_ROLE,
    enable_sagemaker=True,
    experiment_name=None,
    trial_name=None,
    spot_instances=False,
    volume_size=30,
    max_run=60*60*12,
    max_wait=60*60*24,
    env=None,
    workers=2,
    output_json=None
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
        Directory to save trained inference model.
        Set default for ``--model-dir``.
    output_dir: string, optional
        Directory to save outputs (images, logs, etc.).
        Set default for ``--output-dir``.
    checkpoint_dir: string, optional
        Directory to save checkpoints for saving and resuming training.
        Set default for ``--checkpoint-dir``.
    checkpoint_s3: string, optional
        S3 storage for checkpoints for saving and resuming training or "default".
        Set default for ``--sagemaker-checkpoint-s3``.
    checkpoint_container: string, optional
        Local directory for checkpoints when running remotely.
        Set default for ``--sagemaker-checkpoint-container``.
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
    max_run : int, optional
        Maximum training time in seconds.
    max_wait : int, optional
        Maximum time to wait for a spot instance in seconds.
    workers : int, optional
        Number of workers
    """
    if isinstance(script, types.FunctionType):
        script = inspect.getfile(script)
    config = SageMakerTrainingConfig(
        inputs=inputs, dependencies=dependencies, env=env)
    if enable_sagemaker:
        group = parser.add_argument_group(
            title='SageMaker', description='SageMaker options'
        )
        sagemaker_profile_args(parser=group, profile=profile)
        bool_argument(group, '--sagemaker-run', default=run,
                      help="Run training on SageMaker (yes/no default={})".format(run))
        bool_argument(group, '--sagemaker-wait', default=wait,
                      help="Wait for SageMaker training to complete and tail logs files (yes/no default={})".format(wait))
        bool_argument(group, '--sagemaker-spot-instances', default=spot_instances,
                      help="Use spot instances for training (yes/no default={})".format(spot_instances))
        group.add_argument(
            '--sagemaker-script',
            default=script,
            help='Script to run on SageMaker. (default: [{}])'.format(script))
        group.add_argument(
            '--sagemaker-source',
            default=source,
            help='Source to upload to SageMaker. '
            'Must contain script. '
            'If blank, default to directory containing script. '
            '(default: [{}])'.format(source))
        group.add_argument(
            '--sagemaker-training-instance',
            default=training_instance,
            help='Instance type for training')
        group.add_argument(
            '--sagemaker-training-image',
            default=training_image,
            help='Docker image for training')
        group.add_argument(
            '--sagemaker-training-image-path',
            default=training_image_path,
            help='Path to dockerfile if image does not exist')
        group.add_argument(
            '--sagemaker-training-image-accounts',
            default=training_image_accounts,
            help='Accounts for docker build')
        group.add_argument(
            '--sagemaker-training-role',
            default=training_role,
            help='Docker image for training')
        group.add_argument(
            '--sagemaker-base-job-name',
            default=base_job_name,
            help='Base job name for tracking and organization on S3.'
            ' A job name will be generated from the base job name unless a job name is specified.')
        group.add_argument(
            '--sagemaker-job-name',
            default=job_name,
            help='Job name for tracking. Use --base-job-name instead and a job name will be automatically generated with a timestamp.')
        group.add_argument(
            '--sagemaker-experiment-name',
            default=experiment_name,
            help='Name of experiment in SageMaker tracking.')
        group.add_argument(
            '--sagemaker-trial-name',
            default=trial_name,
            help='Name of experiment trial in SageMaker tracking.')
        group.add_argument(
            '--sagemaker-volume-size',
            type=int,
            default=volume_size,
            help='Volume size in GB.')
        group.add_argument(
            '--sagemaker-max-run',
            type=int,
            default=max_run,
            help='Maximum runtime in seconds.')
        group.add_argument(
            '--sagemaker-max-wait',
            type=int,
            default=max_wait,
            help='Maximum time to wait for spot instances in seconds.')
        group.add_argument(
            '--sagemaker-output-json',
            type=str,
            default=output_json,
            help='Output job details to JSON file.')

        sagemaker_training_dependency_args(
            parser=parser, dependencies=config.dependencies)
    sagemaker_training_model_args(parser=parser, model_dir=model_dir)
    sagemaker_training_output_args(parser=parser, output_dir=output_dir)
    sagemaker_training_checkpoint_args(
        parser=parser,
        checkpoint_dir=checkpoint_dir,
        checkpoint_s3=checkpoint_s3,
        checkpoint_container=checkpoint_container,
        checkpoint_initial=checkpoint_initial,
        enable_sagemaker=enable_sagemaker)
    sagemaker_training_channel_args(parser=parser, inputs=config.inputs)
    if additional_arguments:
        for args, kwargs in additional_arguments:
            parser.add_argument(*args, **kwargs)
    if argparse_callback:
        argparse_callback(parser)
    return config


def sagemaker_training_output_args(parser: argparse.ArgumentParser, output_dir):
    output_dir = os.environ.get('SM_OUTPUT_DIR', output_dir)
    parser.add_argument('--output-dir', type=str,
                        default=output_dir,
                        help='Directory for logs, images, or other output files (default: "{}")'.format(output_dir))


def sagemaker_training_checkpoint_args(
        parser: argparse.ArgumentParser, checkpoint_dir, checkpoint_initial=None,
        checkpoint_s3='default', checkpoint_container=CHECKPOINT_LOCAL_PATH, enable_sagemaker=True):

    group = parser.add_argument_group(
        title='Checkpoints',
        description='Checkpointing options'
    )
    group.add_argument('--checkpoint-dir', type=str,
                       default=checkpoint_dir,
                       help='Local directory to store checkpoints for resuming training (default: "{}")'.format(checkpoint_dir))
    if enable_sagemaker:
        group.add_argument('--sagemaker-checkpoint-s3', type=str,
                           default=checkpoint_s3,
                           help='Location to store checkpoints on S3 or "default" (default: "{}")'.format(checkpoint_s3))
        group.add_argument('--sagemaker-checkpoint-container', type=str,
                           default=checkpoint_container,
                           help='Location to store checkpoints on container (default: "{}")'.format(checkpoint_container))
        group.add_argument('--checkpoint-initial', type=str,
                           default=checkpoint_initial, help='Initial checkpoint')


def sagemaker_training_dependency_args(parser: argparse.ArgumentParser, dependencies):
    if dependencies:
        group = parser.add_argument_group(
            title='Dependencies',
            description='Dependencies to upload to SageMaker'
        )
        for k, v in dependencies.items():
            flag = variable_to_argparse(k)
            group.add_argument(flag, type=str,
                               default=v,
                               help='Directory for dependency [{}] (default: "{}")'.format(k, v))


def sagemaker_training_channel_args(parser: argparse.ArgumentParser, inputs):
    if inputs and len(inputs):
        group = parser.add_argument_group(
            title='Inputs',
            description='Inputs (local or S3)'
        )
        for channel, default in inputs.items():
            flag = variable_to_argparse(channel)
            # todo: check opts
            #env_key = 'SM_CHANNEL_{}'.format(channel.upper())
            #local = default.local
            # if env_key in os.environ:
            #    local = os.environ[env_key]
            group.add_argument(
                flag,
                type=str,
                default=None if default.repeated else default.local,
                help=CHANNEL_HELP.format(
                    channel=channel,
                    default=default.local),
                action='append' if default.repeated else 'store'
            )
            mode_flag = variable_to_argparse("{}_mode".format(channel))
            group.add_argument(
                mode_flag, type=str,  default=default.mode or "File",
                help=CHANNEL_HELP_MODE.format(channel=channel, default=default.mode or "File"))
            suffix_flag = variable_to_argparse("{}_suffix".format(channel))
            group.add_argument(
                suffix_flag, help=argparse.SUPPRESS, default="", type=str)
            repeat_flag = variable_to_argparse("{}_repeat".format(channel))
            group.add_argument(
                repeat_flag, help="Repeat input", default=default.repeat, type=int)
            shuffle_flag = variable_to_argparse("{}_shuffle".format(channel))
            bool_argument(
                parser, shuffle_flag, help='Shuffle inputs', default=default.shuffle
            )


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
