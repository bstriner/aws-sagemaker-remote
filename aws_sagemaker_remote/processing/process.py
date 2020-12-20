import os
from argparse import ArgumentParser
from pathlib import Path

try:
    from boto3.session import Session as Boto3Session
    from sagemaker.session import Session as SagemakerSession
    from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
except:
    pass
import json

import datetime

from aws_sagemaker_remote.util.cli_argument import cli_argument
from aws_sagemaker_remote.util.json_read import json_converter
from aws_sagemaker_remote.ecr.images import Images, ecr_ensure_image, Image
from ..session import sagemaker_session
from .iam import ensure_processing_role
from ..args import variable_to_argparse, get_local_path, PathArgument
from .args import PROCESSING_INSTANCE, PROCESSING_JOB_NAME, PROCESSING_RUNTIME_SECONDS, INPUT_MOUNT, OUTPUT_MOUNT, MODULE_MOUNT
from .config import SageMakerProcessingConfig
from .args import sagemaker_processing_args
from ..git import git_get_tags
from ..tags import make_tags
from ..s3 import is_s3_file
PROCESSING_SCRIPT = os.path.abspath(os.path.join(__file__, '../processing.sh'))


def sagemaker_processing_run(args, config):
    script = args.sagemaker_script
    script = os.path.abspath(script)
    script = script.replace("\\", "/")

    session = sagemaker_session(profile_name=args.sagemaker_profile)

    inputs = {
        k: PathArgument(
            local=cli_argument(getattr(args, k), session=session),
            optional=v.optional,
            mode=getattr(args, "{}_mode".format(k) or v.mode or 'File')
        ) for k, v in config.inputs.items()
    }
    for k, v in inputs.items():
        if (not v.local) and (not v.optional):
            raise ValueError("Value required for input agument [{}]".format(k))
    inputs = {
        k: v for k, v in inputs.items() if v.local
    }
    outputs = {
        k: PathArgument(
            local=cli_argument(getattr(args, k), session=session),
            remote=cli_argument(
                getattr(args, "{}_s3".format(k)), session=session),
            optional=v.optional,
            mode=getattr(args, "{}_mode".format(k) or v.mode or 'EndOfJob')
        ) for k, v in config.outputs.items()
    }
    # for k, v in outputs.items():
    #    if (not v) and (not config.outputs[k].optional):
    #        raise ValueError(
    #            "Value required for output agument [{}_s3]".format(k))
    # outputs = {
    #    k: v for k, v in outputs.items() if v
    # }
    # todo: optional arguments
    dependencies = {
        k: getattr(args, k) for k in config.dependencies.keys()
    }
    tags = git_get_tags(script)
    process(
        inputs=inputs,
        outputs=outputs,
        dependencies=dependencies,
        session=session,
        role=args.sagemaker_role,
        script=script,
        image=args.sagemaker_image,
        image_path=args.sagemaker_image_path,
        image_accounts=args.sagemaker_image_accounts,
        instance=args.sagemaker_instance,
        base_job_name=args.sagemaker_base_job_name,
        job_name=args.sagemaker_job_name,
        volume_size=args.sagemaker_volume_size,
        python=args.sagemaker_python,
        runtime_seconds=args.sagemaker_runtime_seconds,
        output_mount=args.sagemaker_output_mount if hasattr(
            args, 'sagemaker_output_mount') else None,
        input_mount=args.sagemaker_input_mount if hasattr(
            args, 'sagemaker_input_mount') else None,
        module_mount=args.sagemaker_module_mount if hasattr(
            args, 'sagemaker_module_mount') else None,
        arguments=make_arguments(args=args, config=config),
        requirements=args.sagemaker_requirements,
        configuration_script=args.sagemaker_configuration_script,
        configuration_command=args.sagemaker_configuration_command,
        wait=args.sagemaker_wait,
        tags=tags,
        output_json=args.sagemaker_output_json,
        env=config.env
    )


def make_arguments(args, config: SageMakerProcessingConfig):
    vargs = vars(args)
    # , 'sagemaker_role', 'sagemaker_profile']
    to_del = ['sagemaker_run', 'sagemaker_job_name']
    to_del.extend(config.inputs.keys())
    to_del.extend(config.outputs.keys())
    to_del.extend("{}_s3" for k in config.outputs.keys())
    to_del.extend(config.dependencies.keys())
    for k in to_del:
        if k in vargs:
            del vargs[k]
    vargs['sagemaker_run'] = False
    return vargs


def sagemaker_arguments(vargs):
    arguments = []
    for k, v in vargs.items():
        if v is not None:
            v = str(v)
            if len(v) > 0:
                arguments.extend(
                    [variable_to_argparse(k), str(v)]
                )
    return arguments


def ensure_eol(file):
    """
    Ensure that file has Linux line endings. Convert if it doesn't.
    """
    if b"\r\n" in open(file, 'rb').read():
        print("DOS line endings found in {}. Attempting conversion.".format(file))
        with open(file, 'U') as infile:
            text = infile.read()
        with open(file, 'w', newline='\n') as outfile:
            outfile.write(text)


def make_processing_input(mount, name, source, s3, mode=None):
    destination = "{}/{}".format(mount, name)
    if mode:
        assert mode in ['File', 'Pipe']
    processing_input = ProcessingInput(
        source=source,
        destination=destination,
        input_name=name,
        # s3_data_type='S3Prefix',
        s3_input_mode=mode or 'File',
        # s3_data_distribution_type='FullyReplicated',
        # s3_compression_type='None'
    )
    path = get_local_path(source)
    if path:
        if not os.path.exists(path):
            raise ValueError(
                "Local path [{}]: [{}] does not exist".format(name, source))
        if os.path.isfile(path):
            basename = os.path.basename(path)
            path_argument = "{}/{}".format(destination, basename)
        elif os.path.isdir(path):
            path_argument = destination
        else:
            raise ValueError(
                "Local path [{}] is neither file nor directory".format(source))
    else:
        if is_s3_file(source, s3=s3):
            basename = os.path.basename(source)
            path_argument = "{}/{}".format(destination, basename)
        else:
            path_argument = destination
    return processing_input, path_argument


def process(
    session: SagemakerSession,
    role,
    script,
    # script_source,
    inputs=None,
    outputs=None,
    dependencies=None,
    requirements=None,
    configuration_script=None,
    configuration_command=None,
    base_job_name=PROCESSING_JOB_NAME,
    job_name=None,
    image=Images.PROCESSING.tag,
    image_path=Images.PROCESSING.path,
    image_accounts=",".join(Images.PROCESSING.accounts),
    instance=PROCESSING_INSTANCE,
    volume_size=30,
    runtime_seconds=PROCESSING_RUNTIME_SECONDS,
    output_mount=OUTPUT_MOUNT,
    input_mount=INPUT_MOUNT,
    module_mount=MODULE_MOUNT,
    python='python3',
    wait=True,
    logs=True,
    arguments=None,
    tags=None,
    output_json=None,
    env=None
):
    iam = session.boto_session.client('iam')

    image_uri = ecr_ensure_image(
        image=Image(
            path=image_path,
            tag=image,
            accounts=image_accounts.split(",")
        ),
        session=session.boto_session
    )
    role = ensure_processing_role(iam=iam, role_name=role)
    if inputs is None:
        inputs = {}
    if outputs is None:
        outputs = {}
    if dependencies is None:
        dependencies = {}
    if tags is None:
        tags = {}
    else:
        tags = tags.copy()
    if arguments is None:
        arguments = {}
    else:
        arguments = arguments.copy()
    # if module_mount is not None and len(module_mount)> 0:
    #    command = ["PYTHONPATH={module_mount};${{PYTHONPATH}}".format(module_mount=module_mount), "python3"]
    # else:
    #    command = ['python3']
    command = ['sh']
    path_arguments = {}
    processing_inputs = []
    s3 = session.boto_session.client('s3')
    for name, source in inputs.items():
        processing_input, path_argument = make_processing_input(
            mount=input_mount,
            name=name,
            source=source.local,
            mode=source.mode,
            s3=s3
        )
        processing_inputs.append(processing_input)
        path_arguments[name] = path_argument
    for name, source in dependencies.items():
        processing_input, path_argument = make_processing_input(
            mount=module_mount,
            name=name,
            source=source,
            s3=s3
        )
        processing_inputs.append(processing_input)
        path_arguments[name] = path_argument

    script_remote = "{}/{}".format(module_mount, os.path.basename(script))
    processing_inputs.append(
        ProcessingInput(
            source=script,
            destination=module_mount,
            input_name="aws_sagemaker_remote_script",
            # s3_data_type='S3Prefix',
            s3_input_mode='File',
            # s3_data_distribution_type='FullyReplicated',
            # s3_compression_type='None'
        )
    )
    if env:
        env = env.copy()
    else:
        env = {}
    env.update({
        "AWS_SAGEMAKER_REMOTE_MODULE_MOUNT": module_mount,
        "AWS_SAGEMAKER_REMOTE_PYTHON": python,
        "AWS_SAGEMAKER_REMOTE_SCRIPT": script_remote,
        "IS_SAGEMAKER": "1"
    })

    if requirements:
        requirements_remote = "{}/requirements_txt/{}".format(
            module_mount, 'requirements.txt')
        env['AWS_SAGEMAKER_REMOTE_REQUIREMENTS'] = requirements_remote
        processing_inputs.append(
            ProcessingInput(
                source=requirements,
                destination="{}/requirements_txt".format(module_mount),
                input_name="aws_sagemaker_remote_requirements",
                s3_input_mode='File',
            )
        )

    if configuration_script:
        configuration_script_remote = "{}/{}".format(
            module_mount, os.path.basename(configuration_script))
        env['AWS_SAGEMAKER_REMOTE_CONFIGURATION_SCRIPT'] = configuration_script_remote
        processing_inputs.append(
            ProcessingInput(
                source=configuration_script,
                destination=module_mount,
                input_name="aws_sagemaker_remote_configuration_script",
                s3_input_mode='File'
            )
        )

    if configuration_command and len(configuration_command) > 0:
        env['AWS_SAGEMAKER_REMOTE_CONFIGURATION_COMMAND'] = configuration_command

    tags["Source"] = 'aws-sagemaker-remote'
    tags["BaseJobName"] = base_job_name
    tags = make_tags(tags)
    print("Tags: {}".format(tags))
    processor = ScriptProcessor(
        role,
        image_uri=image_uri,
        instance_count=1,
        instance_type=instance,
        command=command,
        volume_size_in_gb=volume_size,
        # volume_kms_key=None,
        # output_kms_key=None,
        max_runtime_in_seconds=runtime_seconds,
        base_job_name=base_job_name,
        sagemaker_session=session,
        env=env,
        tags=tags
        # network_config=None
    )
    processing_outputs = []
    for name, dest in outputs.items():
        # todo: move into PathArgument class
        if not ((not dest.remote) or dest.remote == 'default' or dest.remote.startswith('s3://')):
            raise ValueError("Argument [{}] must be either `default` or an S3 url (`s3://...`). Value given was [{}].".format(
                variable_to_argparse("{}_s3".format(name)), dest.remote))
        source = "{}/{}".format(output_mount, name)
        if dest.mode:
            assert dest.mode in ['EndOfJob', 'Continuous']
        processing_outputs.append(
            ProcessingOutput(
                source=source,
                destination=dest.remote if dest.remote and dest.remote != 'default' else None,
                output_name=name,
                s3_upload_mode=dest.mode or 'EndOfJob'
            ))
        path_arguments[name] = source

    ensure_eol(PROCESSING_SCRIPT)
    code = Path(PROCESSING_SCRIPT).as_uri()
    if job_name is None or len(str(job_name).strip()) == 0:
        job_name = None
    else:
        job_name = str(job_name).strip()

    arguments.update(path_arguments)
    processor.run(
        code=code,
        inputs=processing_inputs,
        outputs=processing_outputs,
        wait=False,
        logs=logs,
        job_name=job_name,
        arguments=sagemaker_arguments(vargs=arguments)
    )
    job = processor.latest_job
    if output_json:
        obj = job.describe()
        #print("Describe: {}".format(obj))
        os.makedirs(os.path.dirname(
            os.path.abspath(output_json)), exist_ok=True)
        with open(output_json, 'w') as f:
            json.dump(obj, f, default=json_converter, indent=4)

    if wait:
        job.wait(logs=logs)
    return processor
