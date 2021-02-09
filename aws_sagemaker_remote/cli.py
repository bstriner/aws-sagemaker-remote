import click
import sagemaker
import boto3
import logging
import os
from aws_sagemaker_remote.util.upload import upload
from aws_sagemaker_remote.util.concat import s3_concat
from aws_sagemaker_remote.util.json_read import json_read
from aws_sagemaker_remote.util.cli_argument import cli_argument
from aws_sagemaker_remote.ecr.images import Images, ecr_build_image, Image
from aws_sagemaker_remote.util.training import training_describe
from aws_sagemaker_remote.util.processing import processing_describe
from aws_sagemaker_remote.inference.model import model_create, model_delete, model_describe
from aws_sagemaker_remote.inference.endpoint import endpoint_create, endpoint_delete, endpoint_describe, endpoint_invoke
from aws_sagemaker_remote.inference.endpoint_config import endpoint_config_create, endpoint_config_delete, endpoint_config_describe
from aws_sagemaker_remote.batch.report import batch_report
from aws_sagemaker_remote.transform.transform import transform_create

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

current_profile = None


@click.group()
@click.option('--profile', help='AWS profile. Run `aws-configure` to configure a profile.', default='default')
def cli(profile='default'):
    """
    Set of utilities for managing AWS training, processing, and more.
    """
    global current_profile
    current_profile = profile


@cli.group(name='batch')
def cli_batch():
    """
    S3 batch processing commands
    """
    pass


@cli_batch.command(name='report')
@click.option('--job', type=str, default=[], multiple=True)
@click.option('--output', type=str, default='output/batch-report')
def cli_batch_report(job, output):
    """
    Collate a report of completed and failed operations from one or more batch jobs
    """
    session = boto3.Session(profile_name=current_profile)
    batch_report(
        session=session,
        job=job,
        output=output
    )


@cli.group(name='json')
def cli_json():
    """
    JSON manipulation commands
    """
    pass


@cli_json.command(name='parse', help="""Parse comma-delimited path [PATH]
""")
@click.argument('path')
def cli_json_parse(path):
    """
    Print the resolved value of the first argument according
    to the rules for CSV input processing
    """
    session = boto3.Session(profile_name=current_profile)
    data = cli_argument(path, session=session)
    print(data)


@cli_json.command(name='read', help="""Read field [FIELD] from JSON file at [PATH]
""")
@click.argument('path')
@click.argument('field')
def cli_json_read(path, field):
    """
    Read field [FIELD] from JSON file at [PATH]
    """
    session = boto3.Session(profile_name=current_profile)
    path = cli_argument(path, session=session)
    data = json_read(path, field, session=session)
    print(data)


@cli.group(name="s3")
def cli_s3():
    """
    S3 management commands
    """
    pass


@cli_s3.command(name='upload')
@click.argument('src')
@click.argument('dst')
@click.option('--gz/--no-gz', default=False)
@click.option('--root', type=str, default=".", help="Target path in resulting zip file")
def cli_s3_upload(src, dst, gz, root):
    """
    Upload a file or directory to S3, optionally with GZIP
    """
    session = boto3.Session(profile_name=current_profile)
    session = sagemaker.Session(session)
    upload(src=src, dst=dst, gz=gz, session=session, root=root)


@cli_s3.command(name='concat')
@click.option('--manifest', help="Input manifest file")
@click.option('--limit', type=int, default=0, help="Number of files (0 for all)")
@click.option('--output', type=str, required=True, help="Output file path")
def cli_s3_concat(manifest, limit, output):
    """
    Download and concatenate multiple files from an S3 manifest
    """
    session = boto3.Session(profile_name=current_profile)
    session = sagemaker.Session(session)
    s3_concat(
        manifest=cli_argument(manifest, session=session),
        limit=limit,
        output=output,
        session=session
    )


@cli.group()
def processing():
    """
    Processing commands
    """
    pass


@processing.command(name='describe')
@click.argument(
    'name'
)
@click.argument(
    'field',
    required=False)
def processing_describe_cli(name, field):
    """
    Describe training job NAME.

    * Print full JSON if FIELD is not specified.

    * Print only FIELD if specified (e.g., ModelArtifacts.S3ModelArtifacts or LastModifiedTime).
    """
    session = boto3.Session(profile_name=current_profile)
    session = sagemaker.Session(session)
    description = processing_describe(
        job_name=cli_argument(name, session=session),
        field=field,
        session=session
    )
    print(description)


@cli.group()
def transform():
    """
    SageMaker batch transform commands
    """
    pass


@transform.command(name='create')
@click.option('--base-job-name', help='Transform job base name. If job name not provided, job name is the base job name plus a timestamp.', type=str, default='transform-job')
@click.option('--job-name', help='Transform job name for tracking in AWS console', type=str, default=None)
@click.option('--model-name', help='SageMaker Model name', type=str, default=None, required=True)
@click.option('--concurrency', help='Concurrency (number of concurrent requests to each container)', type=int, default=1)
@click.option('--timeout', help='Timeout in seconds per request', type=int, default=60*5)
@click.option('--retries', help='Number of retries for each failed request', type=int, default=0)
@click.option('--input-s3', help='Input path on S3', type=str, default=None, required=True)
@click.option('--output-s3', help='Output path on S3', type=str, default=None, required=True)
@click.option('--input-type', help='Input MIME type ("Content-Type" header)', type=str, default=None, required=True)
@click.option('--output-type', help='Output MIME type ("Accept" header)', type=str, default=None, required=True)
@click.option('--output-json', help='Save job information in JSON file', type=str, default=None)
@click.option('--instance-type', help='SageMaker Instance type (e.g., ml.m5.large)', type=str, default="ml.m5.large")
@click.option('--instance-count', help='Number of containers to use (processing will be distributed)', type=int, default=1)
@click.option('--payload-mb', help='Maximum payload size (MB)', type=int, default=32)
def transform_create_cli(
        base_job_name,
        job_name,
        model_name,
        concurrency,
        timeout,
        retries,
        input_s3,
        output_s3,
        input_type,
        output_type,
        instance_type,
        instance_count,
        payload_mb,
        output_json):
    """
    Create a batch transformation job for objects in S3

    - Model must already exist in SageMaker
    - Model instances are deployed
    - Each S3 object is posted to one of your instances
    - Results are saved in S3 with the extension ".out"
    - Model instances are destroyed
    """
    transform_create(
        session=boto3.Session(profile_name=current_profile),
        base_job_name=base_job_name,
        job_name=job_name,
        model_name=model_name,
        concurrency=concurrency,
        timeout=timeout,
        retries=retries,
        input_s3=input_s3,
        output_s3=output_s3,
        input_type=input_type,
        output_type=output_type,
        instance_type=instance_type,
        instance_count=instance_count,
        output_json=output_json,
        payload_mb=payload_mb
    )


@cli.group()
def training():
    """
    SageMaker training commands
    """
    pass


@training.command(name='describe')
@click.argument(
    'name'
)
@click.argument(
    'field',
    required=False)
def training_describe_cli(name, field):
    """
    Describe training job NAME. 

    * Print full JSON if FIELD is not specified.

    * Print only FIELD if specified (e.g., ModelArtifacts.S3ModelArtifacts or LastModifiedTime).
    """
    session = boto3.Session(profile_name=current_profile)
    session = sagemaker.Session(session)
    description = training_describe(
        job_name=cli_argument(name, session=session),
        field=field,
        session=session
    )
    print(description)

# Model CLI


@cli.group()
def model():
    """
    Model commands
    """
    pass


@model.command(name='create')
@click.option('--job', help='Job name', type=str, default=None)
@click.option('--model-artifact', help='Model artifact (S3 URI). Relative path assumes default bucket', type=str, default=None)
@click.option('--name', help='Model name', type=str, default=None)
@click.option('--inference-image', help='ECR Docker URI for inference', type=str,
              default=Images.INFERENCE.tag)
@click.option('--inference-image-path', help='Path for building image if necessary', type=str,
              default=Images.INFERENCE.path)
@click.option('--inference-image-accounts', help='Accounts for building image', type=str,
              default=",".join(Images.INFERENCE.accounts))
@click.option('--role', help='SageMaker inference role name', type=str,
              default='aws-sagemaker-remote-inference-role')
@click.option('--force/--no-force', default=False)
@click.option('--multimodel/--singlemodel', default=False, help="SingleModel or MultiModel mode")
def model_create_cli(
        job, model_artifact, name, inference_image,
        inference_image_path, inference_image_accounts, multimodel, role, force):
    """
    Create a SageMaker model
    """
    session = boto3.Session(profile_name=current_profile)
    session = sagemaker.Session(session)
    model_create(
        job=cli_argument(job, session=session),
        model_artifact=cli_argument(model_artifact, session=session),
        name=cli_argument(name, session=session),
        session=session,
        inference_image=cli_argument(inference_image),
        inference_image_path=inference_image_path,
        inference_image_accounts=inference_image_accounts,
        role=role,
        force=force,
        multimodel=multimodel)


@model.command(name='delete')
@click.argument('name')
def model_delete_cli(name):
    """
    Delete SageMaker model NAME
    """
    session = boto3.Session(profile_name=current_profile)
    client = session.client('sagemaker')
    model_delete(name=cli_argument(name, session=session), client=client)


@model.command(name='describe')
@click.argument("name")
@click.argument("field", required=False, default=None)
def model_describe_cli(name, field):
    """
    Describe endpoint configuration NAME
    """
    session = boto3.Session(profile_name=current_profile)
    client = session.client('sagemaker')
    description = model_describe(
        name=cli_argument(name, session=session),
        client=client,
        field=field
    )
    print(description)

# Endpoint config CLI


@cli.group()
def endpoint_config():
    """
    Endpoint config comands
    """
    pass


@endpoint_config.command(name='create')
@click.option('--name', type=str)
@click.option('--model', multiple=True)
@click.option(
    '--instance-type',
    help='SageMaker instance type', type=str,
    default='ml.t2.medium')
@click.option('--force/--no-force', default=False)
def endpoint_config_create_cli(name, model, instance_type, force):
    """
    Create an endpoint configuration
    """
    session = boto3.Session(profile_name=current_profile)
    session = sagemaker.Session(session)
    endpoint_config_create(
        name=cli_argument(name, session=session),
        model=[cli_argument(m, session=session) for m in model],
        instance_type=instance_type,
        force=force,
        session=session)


@endpoint_config.command(name='describe')
@click.argument("name")
@click.argument("field", required=False, default=None)
def endpoint_config_describe_cli(name, field):
    """
    Describe endpoint configuration NAME
    """
    session = boto3.Session(profile_name=current_profile)
    client = session.client('sagemaker')
    description = endpoint_config_describe(
        name=cli_argument(name, session=None),
        client=client,
        field=field
    )
    print(description)


@endpoint_config.command(name='delete')
@click.argument("name")
def endpoint_config_delete_cli(name):
    """
    Delete endpoint configuration NAME
    """
    session = boto3.Session(profile_name=current_profile)
    client = session.client('sagemaker')
    endpoint_config_delete(
        name=cli_argument(name, session=None),
        client=client
    )

# Endpoint CLI


@cli.group()
def endpoint():
    """
    Endpoint commands
    """
    pass


@endpoint.command(name='create')
@click.option('--name', type=str, default=None, help='Name of endpoint')
@click.option('--config', type=str, default=None, help='Name of endpoint config')
@click.option('--force/--no-force', default=False, help='Overwrite existing endpoint')
def endpoint_create_cli(name, config, force):
    """
    Create a SageMaker endpoint
    """
    session = boto3.Session(profile_name=current_profile)
    client = session.client('sagemaker')
    endpoint_create(
        name=cli_argument(name, session=session),
        config=cli_argument(config, session=session),
        force=force,
        client=client)


@endpoint.command(name='delete')
@click.argument('name', type=str)
def endpoint_delete_cli(name):
    """
    Delete a SageMaker endpoint
    """
    session = boto3.Session(profile_name=current_profile)
    client = session.client('sagemaker')
    endpoint_delete(
        name=cli_argument(name, session=session),
        client=client
    )


@endpoint.command(name='describe')
@click.argument('name', type=str)
@click.argument('field', type=str, default=None, required=False)
def endpoint_describe_cli(name, field):
    """
    Describe a SageMaker endpoint
    """
    session = boto3.Session(profile_name=current_profile)
    client = session.client('sagemaker')
    description = endpoint_describe(
        name=cli_argument(name, session=session),
        client=client,
        field=field)
    print(description)


@endpoint.command(name='invoke')
@click.option('--name', type=str, default=None)
@click.option('--model', type=str, default=None)
@click.option('--variant', type=str, default=None)
@click.option('--input', type=str, default=None)
@click.option('--input-glob', type=str, default=None, help='glob pattern if input is directory (e.g., `**/*.wav`)')
@click.option('--output', type=str, default=None)
@click.option('--input-type', type=str, default=None)
@click.option('--output-type', type=str, default=None)
@click.option('--model-dir', type=str, default=None)
def endpoint_invoke_cli(name, model, variant, input, input_glob, output, input_type, output_type, model_dir):
    """
    Invoke a SageMaker endpoint or a SageMaker-style model in a local directory
    """
    session = boto3.Session(profile_name=current_profile)
    runtime_client = session.client('sagemaker-runtime')
    result = endpoint_invoke(
        name=cli_argument(name, session=session),
        model=cli_argument(model, session=session),
        variant=variant,
        input=input,
        input_glob=input_glob,
        output=output,
        input_type=input_type,
        output_type=output_type,
        model_dir=model_dir,
        runtime_client=runtime_client)
    if result:
        print(result)


# ECR CLI


@cli.group()
def ecr():
    """
    ECR commands
    """
    pass


@ecr.group(name='build')
def ecr_build():
    """
    Commands to build ECR images
    """
    pass


@ecr_build.command(name='all')
@click.option('--cache/--no-cache', default=True)
@click.option('--pull/--no-pull', default=True)
@click.option('--push/--no-push', default=True)
def ecr_build_all(cache, pull, push):
    """
    Build all available docker images
    """
    session = boto3.Session(profile_name=current_profile)
    for image in Images.ALL:
        print("Building Image {}".format(image.name))
        ecr_build_image(
            image=image,
            pull=pull,
            push=push,
            session=session
        )


def ecr_image_build_cli(image):
    @ecr_build.command(name=image.name, help=f"Build the [{image.tag}] image")
    @click.option('--path', type=str, default=image.path)
    @click.option('--tag', type=str, default=image.tag)
    @click.option('--account', type=str, default=image.accounts, multiple=True)
    @click.option('--cache/--no-cache', default=True)
    @click.option('--pull/--no-pull', default=True)
    @click.option('--push/--no-push', default=True)
    def fn(path, tag, account, cache, pull, push):
        """
        """
        session = boto3.Session(profile_name=current_profile)
        ecr_build_image(
            image=Image(
                path=path,
                tag=tag,
                accounts=account
            ),
            cache=cache,
            pull=pull,
            push=push,
            session=session
        )
    return fn


for image in Images.ALL:
    ecr_image_build_cli(image)


if __name__ == '__main__':
    cli()
