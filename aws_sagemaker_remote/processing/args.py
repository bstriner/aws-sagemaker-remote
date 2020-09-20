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


def sagemaker_processing_module_args(parser: argparse.ArgumentParser, dependencies=None,
                                     module_mount=MODULE_MOUNT):
    if dependencies is None:
        dependencies = {}
    parser.add_argument(
        '--sagemaker-module-mount',
        default=module_mount,
        help=MODULE_MOUNT_HELP.format(module_mount))
    for k, v in dependencies.items():
        varname = "module_{}".format(k)
        flag = variable_to_argparse(varname)
        parser.add_argument(
            flag,
            default=v,
            help=MODULE_HELP.format(k=k, v=v))


def sagemaker_processing_args(
    parser: argparse.ArgumentParser,
    script,
    run=False,
    wait=True,
    profile=PROFILE,
    role=PROCESSING_ROLE,
    image=PROCESSING_IMAGE,
    instance=PROCESSING_INSTANCE,
    inputs=None,
    outputs=None,
    dependencies=None,
    input_mount=INPUT_MOUNT,
    output_mount=OUTPUT_MOUNT,
    module_mount=MODULE_MOUNT,
    base_job_name=PROCESSING_JOB_NAME,
    job_name='',
    runtime_seconds=PROCESSING_RUNTIME_SECONDS,
    volume_size=PROCESSING_VOLUME_SIZE,
    python='python3',
    requirements=None,
    configuration_script=None,
    configuration_command=None,
    additional_arguments=None,
    argparse_callback=None
):
    r"""
    Configure ``argparse.ArgumentParser`` for processing scripts.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        Parser to configure
    script : str
        Path to script file to execute.
        Set default for ``--sagemaker-script``
    run : bool, optional
        Run on SageMaker. 
        Set default for ``--sagemaker-run``.
    wait : bool, optional
        Wait for SageMaker processing to complete. 
        Set default for ``--sagemaker-wait``.
    profile : str, optional
        AWS profile to use for session. 
        Set default for ``--sagemaker-profile``.
    role : str, optional
        AWS IAM role name to use for processing. Will be created if it does not exist. 
        Set default for ``--sagemaker-role``.
    image : str, optional
        URI of ECR Docker image to use for processing. 
        Set default for ``--sagemaker-image``.
    instance : str, optional
        Type of instance to use for processing (e.g., ``ml.t3.medium``). 
        Set default for ``--sagemaker-instance``.
    inputs : dict(str,str), optional
        Dictionary of input arguments.
        For eack key and value, create an argument ``--key`` that defaults to value.

        * Running locally, input arguments are unmodified.
        * Running remotely, inputs are set to appropriate SageMaker mount points. Local inputs are uploaded automatically.
    outputs : dict(str, tuple(str))
        Dictionary of output arguments.
        For eack key:

            * Create an argument ``--key`` that defaults to value[0]. This controls an output path.
            * Create an argument ``--key-s3`` that defaults to value[1]. This controls where output is stored on S3.
              * Set to ``default`` to automatically create an output path based on the job name
              * Set to an S3 URL to store output at a specific location on S3
    dependencies : dict(str, str)
        Dictionary of modules.
        For eack key and value, create an argument ``--module-key`` that defaults to value. 
        This controls the path of a dependency of your code.
        The files at the given path will be uploaded to S3, downloaded to SageMaker, and put on PYTHONPATH.    
    input_mount : str, optional
        Local path on SageMaker container where inputs are downloaded.
        Set default for ``--sagemaker-input-mount``.
    output_mount : str, optional
        Local path on SageMaker container where outputs are written before upload.
        Set default for ``--sagemaker-output-mount``.
    module_mount : str, optional
        Local path on SageMaker container where source code is downloaded. Mount point is put on PYTHONPATH.
        Set default for ``--sagemaker-module-mount``.
    base_job_name : str, optional
        Job name will be generated from ``base_job_name`` and a timestamp if ``job_name`` is not provided.
        Set default for ``--sagemaker-base-job-name``.
    job_name : str, optional
        Job name is used for tracking and organization. 
        Generated from ``base_job_name`` if not provided.
        Use ``base_job_name`` and leave ``job_name`` blank for most use-cases.
        Set default for ``--sagemaker-job-name``.
    runtime_seconds: int, optional
        Maximum in seconds before killing job.
        Set default for ``--sagemaker-runtime-seconds``.
    volume_size: int, optional
        Volume size in GB.
        Set default for ``--sagemaker-volume-size``.
    python: str, optional
        Pyton executable on container (default: ``python3``).
        Set default for ``--sagemaker-python``.
    requirements: str, optional
        Set path to requirements file to upload and install with ``pip install -r``.
        Set default for ``--sagemaker-requirements``.
    configuration_script: str, optional
        Set path to bash script to upload and source.
        Set default for ``--sagemaker-configuration-script``.
    configuration_command: str, optional
        Set command to be run to configure container,
        e.g. ``pip install mypackage && export MYVAR=MYVALUE``.
        Set default for ``--sagemaker-configuration-command``.
    additional_arguments: list, optional
        List of tuple of positional args and keyword args for ``argparse.ArgumentParser.add_argument``.
        Use to add additional arguments to the script.
    argparse_callback: function, optional
        Function accepting one argument ``parser:argparse.ArgumentParser`` that adds additional arguments.
        Use to add additional arguments to the script.
    """
    if additional_arguments is None:
        additional_arguments = []
    sagemaker_profile_args(parser=parser, profile=profile)
    bool_argument(parser, '--sagemaker-run', default=run,
                  help="Run processing on SageMaker (yes/no default={})".format(run))
    bool_argument(parser, '--sagemaker-wait', default=wait,
                  help="Wait for SageMaker processing to complete and tail logs (yes/no default={})".format(wait))
    parser.add_argument('--sagemaker-script', default=script,
                        help='Python script to execute (default: [{}])'.format(script))
    parser.add_argument('--sagemaker-python', default=python,
                        help='Python executable to use in container (default: [{}])'.format(python))
    parser.add_argument('--sagemaker-job-name', default=job_name,
                        help='Job name for SageMaker processing. '
                        'If not provided, will be generated from base job name. '
                        'Leave blank for most use-cases. '
                        '(default: [{}])'.format(job_name))
    parser.add_argument('--sagemaker-base-job-name', default=base_job_name,
                        help='Base job name for SageMaker processing .'
                        'Job name will be generated from the base name and a timestamp '
                        '(default: [{}])'.format(base_job_name))
    parser.add_argument('--sagemaker-runtime-seconds', default=runtime_seconds,
                        help='SageMaker maximum runtime in seconds (default: [{}])'.format(runtime_seconds))
    parser.add_argument('--sagemaker-role', default=role,
                        help='AWS role for SageMaker execution (default: [{}])'.format(role))
    parser.add_argument('--sagemaker-requirements', default=requirements,
                        help='Requirements file to install on SageMaker (default: [{}])'.format(requirements))
    parser.add_argument('--sagemaker-configuration-script', default=configuration_script,
                        help='Bash configuration script to source on SageMaker (default: [{}])'.format(configuration_script))
    parser.add_argument('--sagemaker-configuration-command', default=configuration_command,
                        help='Bash command to run on SageMaker for configuration '
                        '(e.g., ``pip install aws_sagemaker_remote && export MYVAR=MYVALUE``) '
                        '(default: [{}])'.format(configuration_command))
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
        dependencies=dependencies,
        module_mount=module_mount
    )
    for args, kwargs in additional_arguments:
        parser.add_argument(*args, **kwargs)
    if argparse_callback:
        argparse_callback(parser)
    return SageMakerProcessingConfig(
        dependencies=dependencies,
        inputs=inputs,
        outputs=outputs
    )


def sagemaker_processing_parser_for_docs():
    parser = argparse.ArgumentParser()
    script = 'script.py'
    sagemaker_processing_args(
        parser=parser,
        script=script,
        inputs={
            'input': '/path/to/input'
        },
        outputs={
            'output': ('/path/to/output', 'default')
        },
        dependencies={
            'my_module': '/path/to/my_module'
        }
    )
    return parser
