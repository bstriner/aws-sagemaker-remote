import os
from argparse import ArgumentParser
from pathlib import Path

try:
    from boto3.session import Session as Boto3Session
    from sagemaker.session import Session as SagemakerSession
    from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
except:
    pass

from ..session import sagemaker_session
from .iam import ensure_processing_role
from ..args import variable_to_argparse
from .args import PROCESSING_INSTANCE, PROCESSING_IMAGE, PROCESSING_JOB_NAME, PROCESSING_RUNTIME_SECONDS, INPUT_MOUNT, OUTPUT_MOUNT, MODULE_MOUNT
from .config import SageMakerProcessingConfig
from .args import sagemaker_processing_args
PROCESSING_SCRIPT = os.path.abspath(os.path.join(__file__, '../processing.sh'))


def sagemaker_processing_run(args, config):
    script = args.sagemaker_script
    script = os.path.abspath(script)
    script = script.replace("\\", "/")

    session = sagemaker_session(profile_name=args.sagemaker_profile)
    inputs = {
        k: getattr(args, k) for k in config.inputs.keys()
    }
    outputs = {
        k: (getattr(args, k), getattr(args, "{}_s3".format(k))) for k in config.outputs.keys()
    }
    dependencies = {
        k: getattr(args, "module_{}".format(k)) for k in config.dependencies.keys()
    }
    process(
        inputs=inputs,
        outputs=outputs,
        dependencies=dependencies,
        session=session,
        role=args.sagemaker_role,
        script=script,
        image=args.sagemaker_image,
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
        configuration_command=args.sagemaker_configuration_command
    )


def make_arguments(args, config: SageMakerProcessingConfig):
    vargs = vars(args)
    to_del = ['sagemaker_run']  # , 'sagemaker_role', 'sagemaker_profile']
    to_del.extend(config.inputs.keys())
    to_del.extend(config.outputs.keys())
    to_del.extend("{}_s3" for k in config.outputs.keys())
    to_del.extend("module_{}".format(k) for k in config.dependencies.keys())
    for k in to_del:
        if k in vargs:
            del vargs[k]
    vargs['sagemaker_run'] = False
    for k in config.inputs.keys():
        vargs[k] = "{}/{}".format(args.sagemaker_input_mount, k)
    for k in config.outputs.keys():
        vargs[k] = "{}/{}".format(args.sagemaker_output_mount, k)
    arguments = []
    for k, v in vargs.items():
        if v is not None:
            v = str(v)
            if len(v) > 0:
                arguments.extend(
                    [variable_to_argparse(k), str(v)]
                )
    return arguments


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
    image=PROCESSING_IMAGE,
    instance=PROCESSING_INSTANCE,
    volume_size=30,
    runtime_seconds=PROCESSING_RUNTIME_SECONDS,
    output_mount=OUTPUT_MOUNT,
    input_mount=INPUT_MOUNT,
    module_mount=MODULE_MOUNT,
    python='python3',
    wait=True,
    logs=True,
    arguments=None
):
    iam = session.boto_session.client('iam')
    role = ensure_processing_role(iam=iam, role_name=role)
    if inputs is None:
        inputs = {}
    if outputs is None:
        outputs = {}
    if dependencies is None:
        dependencies = {}
    # if module_mount is not None and len(module_mount)> 0:
    #    command = ["PYTHONPATH={module_mount};${{PYTHONPATH}}".format(module_mount=module_mount), "python3"]
    # else:
    #    command = ['python3']
    command = ['sh']
    processing_inputs = [
        ProcessingInput(
            source=source,
            destination="{}/{}".format(input_mount, name),
            input_name=name,
            # s3_data_type='S3Prefix',
            s3_input_mode='File',
            # s3_data_distribution_type='FullyReplicated',
            # s3_compression_type='None'
        )
        for name, source in inputs.items()
    ]
    processing_inputs.extend([
        ProcessingInput(
            source=source,
            destination="{}/{}".format(module_mount, name),
            input_name="module_{}".format(name),
            # s3_data_type='S3Prefix',
            s3_input_mode='File',
            # s3_data_distribution_type='FullyReplicated',
            # s3_compression_type='None'
        )
        for name, source in dependencies.items()
    ])
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
    env = {
        "AWS_SAGEMAKER_REMOTE_MODULE_MOUNT": module_mount,
        "AWS_SAGEMAKER_REMOTE_PYTHON": python,
        "AWS_SAGEMAKER_REMOTE_SCRIPT": script_remote
    }

    if requirements and len(requirements) > 0:
        requirements_remote = "{}/requirements_txt/{}".format(module_mount, 'requirements.txt')
        env['AWS_SAGEMAKER_REMOTE_REQUIREMENTS'] = requirements_remote
        processing_inputs.append(
            ProcessingInput(
                source=requirements,
                destination="{}/requirements_txt".format(module_mount),
                input_name="aws_sagemaker_remote_requirements",
                s3_input_mode='File',
            )
        )

    if configuration_script and len(configuration_script) > 0:
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

    processor = ScriptProcessor(
        role,
        image_uri=image,
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
        tags=[
            {
                "Key": "Source",
                "Value": 'aws-sagemaker-remote'
            },
            {
                "Key": "Name",
                "Value": base_job_name
            }
        ]
        # network_config=None
    )
    for name, dest in outputs.items():
        if not (dest[1] == 'default' or dest[1].startswith('s3://')):
            raise ValueError("Argument [{}] must be either `default` or an S3 url (`s3://...`). Value given was [{}].".format(
                variable_to_argparse("{}_s3".format(name)), dest[1]))
    processing_outputs = [
        ProcessingOutput(
            # source=v,
            source="{}/{}".format(output_mount, name),
            destination=dest[1] if dest[1] and len(
                dest[1]) > 0 and dest[1] != 'default' else None,
            output_name=name,
            s3_upload_mode='EndOfJob'
        )
        for name, dest in outputs.items()
    ]
    code = Path(PROCESSING_SCRIPT).as_uri()
    if job_name is None or len(str(job_name).strip()) == 0:
        job_name = None
    else:
        job_name = str(job_name).strip()
    processor.run(
        code=code,
        inputs=processing_inputs,
        outputs=processing_outputs,
        wait=wait,
        logs=logs,
        job_name=job_name,
        arguments=arguments
    )
    return processor
