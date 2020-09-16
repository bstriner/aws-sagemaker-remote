import argparse
from distutils.util import strtobool
import os
from .config import SageMakerProcessingConfig
from ..args import variable_to_argparse, bool_argument, sagemaker_profile_args, PROFILE

#PROCESSING_IMAGE = '137112412989.dkr.ecr.us-east-1.amazonaws.com/amazonlinux:latest'
PROCESSING_ROLE = 'aws-sagemaker-remote-processing-role'
PROCESSING_IMAGE = '683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo-compute:latest'
PROCESSING_INSTANCE = 'ml.t3.medium'
PROCESSING_JOB_NAME = 'processing-job'
PROCESSING_RUNTIME_SECONDS = 60*60  # 1 hour
PROCESSING_VOLUME_SIZE = 30  # GB

MODULE_MOUNT = '/opt/ml/processing/modules'
MODULE_MOUNT_HELP = """Mount point for modules.
If running on SageMaker, modules are mounted here and this directory is added to PYTHONPATH
(default: [{}])
"""
MODULE_HELP = """Directory of [{k}] module.
If running on SageMaker, modules are uploaded and placed on PYTHONPATH.
(default: [{v}])
"""

INPUT_MOUNT = '/opt/ml/processing/input'
INPUT_MOUNT_HELP = """Mount point for inputs.
If running on SageMaker, inputs are mounted here.
If running locally, S3 inputs are downloaded here. 
No effect on local inputs when running locally.
(default: [{}])
"""
INPUT_HELP = """Input [{k}].
Local path or path on S3.
If running locally, local paths are used directly.
If running locally, S3 paths are downloaded to [`--sagemaker-input-mount`/{k}].
If running on SageMaker, local paths are uploaded to S3 then S3 data is downloaded to [`--sagemaker-input-mount`/{k}].
If running on SageMaker, S3 paths are downloaded to [`--sagemaker-input-mount`/{k}].
(default: [{v}])
"""

OUTPUT_MOUNT = '/opt/ml/processing/output'
OUTPUT_MOUNT_HELP = """Mount point for outputs.
If running on SageMaker, outputs written here are uploaded to S3.
If running locally, S3 outputs written here are uploaded to S3. 
No effect on local outputs when running locally.
(default: [{}])
"""
OUTPUT_HELP = """Output [{k}] local path.
If running locally, set to a local path.
(default: [{v}])
"""
OUTPUT_S3_HELP = """Output [{k}] S3 URI.
Upload results to this URI. Empty string automatically generates a URI.
(default: [{v}])
"""


def sagemaker_processing_input_args(parser: argparse.ArgumentParser, inputs=None,
                                    input_mount=INPUT_MOUNT):
    if inputs is None:
        inputs = {}
    if len(inputs) > 0:
        parser.add_argument(
            '--sagemaker-input-mount',
            default=input_mount,
            help=INPUT_MOUNT_HELP.format(input_mount))
        for k, v in inputs.items():
            flag = variable_to_argparse(k)
            parser.add_argument(
                flag,
                default=v,
                help=INPUT_HELP.format(k=k, v=v))


def sagemaker_processing_output_args(parser: argparse.ArgumentParser, outputs=None,
                                     output_mount=OUTPUT_MOUNT):
    if outputs is None:
        outputs = {}
    if len(outputs) > 0:
        parser.add_argument(
            '--sagemaker-output-mount',
            default=output_mount,
            help=OUTPUT_MOUNT_HELP.format(output_mount))
        for k, v in outputs.items():
            local_default, s3_default = v
            flag = variable_to_argparse(k)
            parser.add_argument(
                flag,
                default=local_default,
                help=OUTPUT_HELP.format(k=k, v=local_default))
            parser.add_argument(
                variable_to_argparse("{}_s3".format(k)),
                default=s3_default,
                help=OUTPUT_S3_HELP.format(k=k, v=s3_default))


def sagemaker_processing_module_args(parser: argparse.ArgumentParser, modules=None,
                                     module_mount=MODULE_MOUNT):
    if modules is None:
        modules = {}
    parser.add_argument(
        '--sagemaker-module-mount',
        default=module_mount,
        help=MODULE_MOUNT_HELP.format(module_mount))
    for k, v in modules.items():
        varname = "module_{}".format(k)
        flag = variable_to_argparse(varname)
        parser.add_argument(
            flag,
            default=v,
            help=MODULE_HELP.format(k=k, v=v))


def sagemaker_processing_args(
    parser: argparse.ArgumentParser,
    run: True,
    profile=PROFILE,
    role=PROCESSING_ROLE,
    image=PROCESSING_IMAGE,
    instance=PROCESSING_INSTANCE,
    inputs=None,
    outputs=None,
    modules=None,
    input_mount=INPUT_MOUNT,
    output_mount=OUTPUT_MOUNT,
    module_mount=MODULE_MOUNT,
    job_name=PROCESSING_JOB_NAME,
    runtime_seconds=PROCESSING_RUNTIME_SECONDS,
    volume_size=PROCESSING_VOLUME_SIZE,
    python='python3',
    requirements=None,
    configuration_script=None,
    additional_arguments=None,
    argparse_callback=None
):
    if additional_arguments is None:
        additional_arguments = []
    sagemaker_profile_args(parser=parser, profile=profile)
    bool_argument(parser, '--sagemaker-run', default=run,
                  help="Run processing on SageMaker (yes/no default={})".format(run))
    parser.add_argument('--sagemaker-python', default=python,
                        help='Python executable to use in container (default: [{}])'.format(python))
    parser.add_argument('--sagemaker-job-name', default=job_name,
                        help='Job name for SageMaker processing (default: [{}])'.format(job_name))
    parser.add_argument('--sagemaker-runtime-seconds', default=runtime_seconds,
                        help='SageMaker maximum runtime in seconds (default: [{}])'.format(runtime_seconds))
    parser.add_argument('--sagemaker-role', default=role,
                        help='AWS role for SageMaker execution (default: [{}])'.format(role))
    parser.add_argument('--sagemaker-requirements', default=requirements,
                        help='Requirements file to install on SageMaker (default: [{}])'.format(requirements))
    parser.add_argument('--sagemaker-configuration-script', default=configuration_script,
                        help='Bash configuration script to source on SageMaker (default: [{}])'.format(configuration_script))
    parser.add_argument('--sagemaker-image', default=image,
                        help='AWS ECR image URI of Docker image to run SageMaker processing (default: [{}])'.format(image))
    parser.add_argument('--sagemaker-instance', default=instance,
                        help='AWS SageMaker instance to run processing (default: [{}])'.format(instance))
    parser.add_argument('--sagemaker-volume-size', default=volume_size,
                        help='AWS SageMaker volume size in GB (default: [{}])'.format(volume_size))
    sagemaker_processing_input_args(
        parser=parser,
        inputs=inputs,
        input_mount=input_mount
    )
    sagemaker_processing_output_args(
        parser=parser,
        outputs=outputs,
        output_mount=output_mount
    )
    sagemaker_processing_module_args(
        parser=parser,
        modules=modules,
        module_mount=module_mount
    )
    for args, kwargs in additional_arguments:
        parser.add_argument(*args, **kwargs)
    if argparse_callback:
        argparse_callback(parser)
    return SageMakerProcessingConfig(
        modules=modules,
        inputs=inputs,
        outputs=outputs
    )

    """
    if channels is None:
        channels = DEFAULT_CHANNELS
    if device is None:
        device = "cpu" if not torch.cuda.is_available() else "cuda"
    output_dir = os.environ.get('SM_OUTPUT_DIR', output_dir)
    parser.add_argument("--device", type=str, default=device,
                        help="device to use (default: {})".format(device))
    parser.add_argument('--output-dir', type=str,
                        default=output_dir,
                        help='directory for checkpoints, logs, images, or other output files (default: "{}")'.format(output_dir))
    for channel, default in channels.items():
        key = 'SM_CHANNEL_{}'.format(channel.upper())
        if key in os.environ:
            default = os.environ[key]
        else:
            default = os.path.abspath(os.path.join(__file__, default))
        parser.add_argument('--{}'.format(channel), type=str,  default=default,
                            help="input directory for [{}] channel".format(channel))
    """


def sagemaker_training_args(
    parser: argparse.ArgumentParser
):
    parser.add_argument("--sagemaker-run", default=False,
                        help="Run training on SageMaker (yes/no default=no)")
