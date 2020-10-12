import click
from aws_sagemaker_remote.util.training import training_describe
from aws_sagemaker_remote.util.processing import processing_describe
from aws_sagemaker_remote.inference.model import model_create, model_delete, model_describe
from aws_sagemaker_remote.inference.endpoint import endpoint_create, endpoint_delete, endpoint_describe, endpoint_invoke
from aws_sagemaker_remote.inference.endpoint_config import endpoint_config_create, endpoint_config_delete, endpoint_config_describe
import sagemaker
import boto3
from aws_sagemaker_remote.util.upload import upload
import logging

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

current_profile = None


@click.group()
@click.option('--profile', help='AWS profile. Run `aws-configure` to configure a profile.', default='default')
def cli(profile='default'):
    global current_profile
    current_profile = profile


@cli.command(name='upload')
@click.argument('src')
@click.argument('dst')
@click.option('--gz/--no-gz', default=False)
def upload_cli(src, dst, gz):
    session = boto3.Session(profile_name=current_profile)
    session = sagemaker.Session(session)
    upload(src=src, dst=dst, gz=gz, session=session)


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
    client = session.client('sagemaker')
    description = processing_describe(
        job_name=name,
        field=field,
        client=client
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
    client = session.client('sagemaker')
    description = training_describe(
        job_name=name,
        field=field,
        client=client
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
              default='683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo-sagemaker-inference:latest')
@click.option('--role', help='SageMaker inference role name', type=str,
              default='aws-sagemaker-remote-inference-role')
@click.option('--force/--no-force', default=False)
def model_create_cli(job, model_artifact, name, inference_image, role, force):
    session = boto3.Session(profile_name=current_profile)
    session = sagemaker.Session(session)
    model_create(
        job=job,
        model_artifact=model_artifact,
        name=name,
        session=session,
        inference_image=inference_image,
        role=role,
        force=force)


@model.command(name='delete')
@click.argument('name')
def model_delete_cli(name):
    """
    Delete SageMaker model NAME
    """
    session = boto3.Session(profile_name=current_profile)
    client = session.client('sagemaker')
    model_delete(name=name, client=client)


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
        name=name,
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
        name=name,
        model=model,
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
        name=name,
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
        name=name,
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
        name=name, config=config, force=force,
        client=client)


@endpoint.command(name='delete')
@click.argument('name', type=str)
def endpoint_delete_cli(name):
    session = boto3.Session(profile_name=current_profile)
    client = session.client('sagemaker')
    endpoint_delete(
        name=name,
        client=client)


@endpoint.command(name='describe')
@click.argument('name', type=str)
@click.argument('field', type=str, default=None, required=False)
def endpoint_describe_cli(name, field):
    session = boto3.Session(profile_name=current_profile)
    client = session.client('sagemaker')
    description = endpoint_describe(
        name=name,
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
        name=name,
        model=model,
        variant=variant,
        input=input,
        output=output,
        input_type=input_type,
        output_type=output_type,
        model_dir=model_dir,
        runtime_client=runtime_client)
    if result:
        print(result)


if __name__ == '__main__':
    cli()
