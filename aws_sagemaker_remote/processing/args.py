import argparse
from distutils.util import strtobool
import os
from .config import SageMakerProcessingConfig
from ..args import variable_to_argparse, bool_argument, sagemaker_profile_args, PROFILE

from aws_sagemaker_remote.ecr.images import Images

PROCESSING_ROLE = 'aws-sagemaker-remote-processing-role'
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
INPUT_MODE_HELP = """Input [{k}] mode. File or Pipe.
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
OUTPUT_MODE_HELP = """Output [{k}] mode.
Set to Continuous or EndOfJob.
(default: [{v}])
"""


def is_sagemaker():
    return os.getenv("IS_SAGEMAKER", False)


def sagemaker_processing_input_args(parser: argparse.ArgumentParser, inputs=None,
                                    input_mount=INPUT_MOUNT):
    if inputs is None:
        inputs = {}
    if len(inputs) > 0:
        group = parser.add_argument_group(
            title='Inputs',
            description='Input options'
        )
        group.add_argument(
            '--sagemaker-input-mount',
            default=input_mount,
            help=INPUT_MOUNT_HELP.format(input_mount))
        for k, v in inputs.items():
            flag = variable_to_argparse(k)
            group.add_argument(
                flag,
                default=v.local,
                help=INPUT_HELP.format(k=k, v=v.local))
            mode = v.mode or 'File'
            group.add_argument(
                variable_to_argparse("{}_mode".format(k)),
                default=mode,
                help=INPUT_MODE_HELP.format(k=k, v=mode))


def sagemaker_processing_output_args(parser: argparse.ArgumentParser, outputs=None,
                                     output_mount=OUTPUT_MOUNT):
    if outputs is None:
        outputs = {}
    if len(outputs) > 0:
        group = parser.add_argument_group(
            title='Output',
            description='Output options'
        )
        group.add_argument(
            '--sagemaker-output-mount',
            default=output_mount,
            help=OUTPUT_MOUNT_HELP.format(output_mount))
        for k, v in outputs.items():
            group.add_argument(
                variable_to_argparse(k),
                default=v.local,
                help=OUTPUT_HELP.format(k=k, v=v.local))
            group.add_argument(
                variable_to_argparse("{}_s3".format(k)),
                default=v.remote,
                help=OUTPUT_S3_HELP.format(k=k, v=v.remote))
            mode = v.mode or 'EndOfJob'
            group.add_argument(
                variable_to_argparse("{}_mode".format(k)),
                default=mode,
                help=OUTPUT_MODE_HELP.format(k=k, v=mode))


def sagemaker_processing_module_args(parser: argparse.ArgumentParser, dependencies=None,
                                     module_mount=MODULE_MOUNT):
    if dependencies is None:
        dependencies = {}
    group = parser.add_argument_group(
        title='Modules', description='Module options'
    )
    group.add_argument(
        '--sagemaker-module-mount',
        default=module_mount,
        help=MODULE_MOUNT_HELP.format(module_mount))
    for k, v in dependencies.items():
        flag = variable_to_argparse(k)
        group.add_argument(
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
    image=Images.PROCESSING.tag,
    image_path=Images.PROCESSING.path,
    image_accounts=",".join(Images.PROCESSING.accounts),
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
    argparse_callback=None,
    output_json=None,
    env=None
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
    image_path : str, optional
        Path to build docker if image does not exist. 
        Set default for ``--sagemaker-image-path``.
    image_accounts : str, optional
        Accounts required to build docker image. 
        Set default for ``--sagemaker-image-accounts``.
    instance : str, optional
        Type of instance to use for processing (e.g., ``ml.t3.medium``). 
        Set default for ``--sagemaker-instance``.
    inputs : dict(str,str), optional
        Dictionary of input argument keys to strings or :class:`aws_sagemaker_remote.args.PathArgument`.
        Strings are converted to ``PathArgument`` with ``local`` set to your string.
        This should be sufficient for most use cases.
        For eack key and value, create an argument ``--key`` that defaults to value.

        * Running locally, input arguments are unmodified.
        * Running remotely, inputs are set to appropriate SageMaker mount points. Local inputs are uploaded automatically.

        For example:

        .. code-block:: python

           import OPTIONAL, PathArgument from aws_sagemaker_remote.args
           inputs = {
               "my_input_1": "path/to/data1", # implicit
               "my_input_2": PathArgument(local="path/to/data2"), # explicit
               "my_optional_input": OPTIONAL
           }

        Your script will now have arguments ``--my-input-1``, ``--my-input-2``, and ``--my-optional-input``.

    outputs : dict(str, str)
        Dictionary of output arguments keys to strings or :class:`aws_sagemaker_remote.args.PathArgument`.
        Strings are converted to ``PathArgument`` with ``local`` set to your string.
        This should be sufficient for most use cases.
        For eack key and value, create an argument ``--key`` that defaults to value.

        For eack key:

            * Create an argument ``--key`` that defaults to ``value.local``. This controls an output path.
            * Create an argument ``--key-s3`` that defaults to ``value.remote``. This controls where output is stored on S3.
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
    output_json: str, optional
        Write SageMaker training details to this path.
        Set default for ``--sagemaker-output-json``
    """
    config = SageMakerProcessingConfig(
        dependencies=dependencies,
        inputs=inputs,
        outputs=outputs,
        env=env
    )

    if additional_arguments is None:
        additional_arguments = []
    group = parser.add_argument_group(
        title='SageMaker', description='SageMaker options'
    )
    sagemaker_profile_args(parser=group, profile=profile)
    bool_argument(group, '--sagemaker-run', default=run,
                  help="Run processing on SageMaker (yes/no default={})".format(run))
    bool_argument(group, '--sagemaker-wait', default=wait,
                  help="Wait for SageMaker processing to complete and tail logs (yes/no default={})".format(wait))
    group.add_argument('--sagemaker-script', default=script,
                       help='Python script to execute (default: [{}])'.format(script))
    group.add_argument('--sagemaker-python', default=python,
                       help='Python executable to use in container (default: [{}])'.format(python))
    group.add_argument('--sagemaker-job-name', default=job_name,
                       help='Job name for SageMaker processing. '
                       'If not provided, will be generated from base job name. '
                       'Leave blank for most use-cases. '
                       '(default: [{}])'.format(job_name))
    group.add_argument('--sagemaker-base-job-name', default=base_job_name,
                       help='Base job name for SageMaker processing .'
                       'Job name will be generated from the base name and a timestamp '
                       '(default: [{}])'.format(base_job_name))
    group.add_argument('--sagemaker-runtime-seconds', default=runtime_seconds, type=int,
                       help='SageMaker maximum runtime in seconds (default: [{}])'.format(runtime_seconds))
    group.add_argument('--sagemaker-role', default=role,
                       help='AWS role for SageMaker execution (default: [{}])'.format(role))
    group.add_argument('--sagemaker-requirements', default=requirements,
                       help='Requirements file to install on SageMaker (default: [{}])'.format(requirements))
    group.add_argument('--sagemaker-configuration-script', default=configuration_script,
                       help='Bash configuration script to source on SageMaker (default: [{}])'.format(configuration_script))
    group.add_argument('--sagemaker-configuration-command', default=configuration_command,
                       help='Bash command to run on SageMaker for configuration '
                       '(e.g., ``pip install aws_sagemaker_remote && export MYVAR=MYVALUE``) '
                       '(default: [{}])'.format(configuration_command))
    group.add_argument('--sagemaker-image', default=image,
                       help='AWS ECR image URI of Docker image to run SageMaker processing (default: [{}])'.format(image))
    group.add_argument('--sagemaker-image-path', default=image_path,
                       help='Path to Dockerfile if image does not exist yet (default: [{}])'.format(image_path))
    group.add_argument('--sagemaker-image-accounts', default=image_accounts,
                       help='Accounts required to build Dockerfile (default: [{}])'.format(image_accounts))
    group.add_argument('--sagemaker-instance', default=instance,
                       help='AWS SageMaker instance to run processing (default: [{}])'.format(instance))
    group.add_argument('--sagemaker-volume-size', default=volume_size, type=int,
                       help='AWS SageMaker volume size in GB (default: [{}])'.format(volume_size))
    group.add_argument('--sagemaker-output-json', default=output_json, type=str,
                       help='Write SageMaker training details to JSON file (default: [{}])'.format(output_json))
    sagemaker_processing_input_args(
        parser=parser,
        inputs=config.inputs,
        input_mount=input_mount
    )
    sagemaker_processing_output_args(
        parser=parser,
        outputs=config.outputs,
        output_mount=output_mount
    )
    sagemaker_processing_module_args(
        parser=parser,
        dependencies=config.dependencies,
        module_mount=module_mount
    )
    if argparse_callback:
        group = parser.add_argument_group(
            title='Processing', description='Processing options'
        )
        argparse_callback(group)
    # todo:
    # for args, kwargs in additional_arguments:
    #    parser.add_argument(*args, **kwargs)
    return config


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
            'output': '/path/to/output'
        },
        dependencies={
            'my_module': '/path/to/my_module'
        }
    )
    return parser
