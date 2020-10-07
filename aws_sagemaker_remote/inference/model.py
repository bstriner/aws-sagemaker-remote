import sagemaker
import click
from botocore.exceptions import ClientError
from aws_sagemaker_remote.util.training import training_describe
from .iam import ensure_inference_role
from aws_sagemaker_remote.util.fields import get_field


def model_delete(name, client):
    client.delete_model(ModelName=name)


def model_describe(name, client, field=None):
    description = client.describe_model(ModelName=name)
    description = get_field(data=description, field=field)
    return description


def model_exists(name, client):
    try:
        model_describe(name=name, client=client)
        return True
    except ClientError:
        return False


def model_create(
    job, model_artifact,
    name, session:sagemaker.Session, inference_image, role, force,
    accelerator_type=None
):
    if (job and model_artifact) or (not (job or model_artifact)):
        raise click.UsageError('Specify one of job_name or model_artifact')
    if model_artifact and not name:
        raise click.UsageError(
            'name is required if job is not provided')
    iam = session.boto_session.client('iam')
    client = session.boto_session.client('sagemaker')
    role = ensure_inference_role(iam=iam, role_name=role)
    if job:
        client = session.boto_session.client('sagemaker')
        model_artifact = training_describe(
            job_name=job,
            field='ModelArtifacts.S3ModelArtifacts',
            client=client
        )
        if not name:
            name = job
        print("Creating model [{}] from job [{}] artifact [{}]".format(
            name, job, model_artifact))
    else:
        if not model_artifact.startswith('s3://'):
            if model_artifact.startswith('/'):
                model_artifact=model_artifact[1:]
            bucket=session.default_bucket()
            model_artifact='s3://{}/{}'.format(bucket, model_artifact)
        print("Creating model [{}] from artifact [{}]".format(
            name, model_artifact))

    if model_exists(name=name, client=client):
        if force:
            print("Deleting existing model")
            model_delete(name=name, client=client)
        else:
            raise click.UsageError('Specify force if overwriting model')
    model = sagemaker.Model(
        image_uri=inference_image,
        model_data=model_artifact,
        role=role,
        predictor_cls=None,
        env=None,
        name=name,
        # vpc_config=None,
        sagemaker_session=session,
        # enable_network_isolation=False,
        # model_kms_key=None
    )
    container_def = sagemaker.container_def(
        model.image_uri,
        model.model_data,
        model.env)

    # self._ensure_base_name_if_needed(container_def["Image"])
    # self._set_model_name_if_needed()

    enable_network_isolation = model.enable_network_isolation()

    # self._init_sagemaker_session_if_does_not_exist(instance_type)
    session.create_model(
        model.name,
        model.role,
        container_def,
        vpc_config=model.vpc_config,
        enable_network_isolation=enable_network_isolation,
        # tags=tags,
    )
