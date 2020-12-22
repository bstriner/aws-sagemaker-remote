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

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

current_profile = None


@click.group()
@click.option('--profile', help='AWS profile. Run `aws-configure` to configure a profile.', default='default')
def cli(profile='default'):
    global current_profile
    current_profile = profile


@cli.group(name='batch')
def cli_batch():
    pass


@cli_batch.command(name='report')
@click.option('--job', type=str, default=[], multiple=True)
@click.option('--output', type=str, default='output/batch-report')
def cli_batch_report(job, output):
    session = boto3.Session(profile_name=current_profile)
    batch_report(
        session=session,
        job=job,
        output=output
    )


@cli.group(name='json')
def cli_json():
    pass


@cli_json.command(name='parse', help="""Parse comma-delimited path [PATH]
""")
@click.argument('path')
def cli_json_parse(path):
    session = boto3.Session(profile_name=current_profile)
    data = cli_argument(path, session=session)
    print(data)


@cli_json.command(name='read', help="""Read field [FIELD] from JSON file at [PATH]
""")
@click.argument('path')
@click.argument('field')
def cli_json_read(path, field):
    session = boto3.Session(profile_name=current_profile)
    path = cli_argument(path, session=session)
    data = json_read(path, field, session=session)
    print(data)


@cli.group(name="s3")
def cli_s3():
    pass


@cli_s3.command(name='upload')
@click.argument('src')
@click.argument('dst')
@click.option('--gz/--no-gz', default=False)
def cli_s3_upload(src, dst, gz):
    session = boto3.Session(profile_name=current_profile)
    session = sagemaker.Session(session)
    upload(src=src, dst=dst, gz=gz, session=session)


@cli_s3.command(name='concat')
@click.option('--manifest')
@click.option('--limit', type=int, default=0)
@click.option('--output', type=str, required=True)
def cli_s3_concat(manifest, limit, output):
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
def training():
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
    Model CLI
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
    Endpoint config CLI
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
    Endpoint CLI
    """
    pass


@endpoint.command(name='create')
@click.option('--name', type=str, default=None, help='Name of endpoint')
@click.option('--config', type=str, default=None, help='Name of endpoint config')
@click.option('--force/--no-force', default=False, help='Overwrite existing endpoint')
def endpoint_create_cli(name, config, force):
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
@click.option('--output', type=str, default=None)
@click.option('--input-type', type=str, default=None)
@click.option('--output-type', type=str, default=None)
@click.option('--model-dir', type=str, default=None)
def endpoint_invoke_cli(name, model, variant, input, output, input_type, output_type, model_dir):
    session = boto3.Session(profile_name=current_profile)
    runtime_client = session.client('sagemaker-runtime')
    result = endpoint_invoke(
        name=cli_argument(name, session=session),
        model=cli_argument(model, session=session),
        variant=variant,
        input=input,
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
    ECR CLI
    """
    pass


@ecr.group(name='build')
def ecr_build():
    """
    """
    pass


@ecr_build.command(name='all')
@click.option('--cache/--no-cache', default=True)
@click.option('--pull/--no-pull', default=True)
@click.option('--push/--no-push', default=True)
def ecr_build_all(cache, pull, push):
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
    @ecr_build.command(name=image.name)
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
