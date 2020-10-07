import sagemaker
import click
import botocore
from aws_sagemaker_remote.util.fields import get_field


def endpoint_config_describe(name, client, field=None):
    description = client.describe_endpoint_config(
        EndpointConfigName=name
    )
    description = get_field(data=description, field=field)
    return description


def endpoint_config_delete(name, client):
    response = client.delete_endpoint_config(
        EndpointConfigName=name
    )
    return response


def endpoint_config_exists(name, client):
    try:
        endpoint_config_describe(name=name, client=client)
        return True
    except botocore.exceptions.ClientError:
        return False


def endpoint_config_create(model, name, instance_type, force, session):
    if not model:
        raise click.UsageError("At least one model must be specified")
    if not name:
        if len(model) == 1:
            name = model[0]
        else:
            raise click.UsageError(
                "Must specifiy endpoint configuration name for multi-model endpoints")

    print("Creating endpoint configuration [{}] from models {}".format(
        name, model
    ))
    client = session.boto_session.client('sagemaker')
    if endpoint_config_exists(name=name, client=client):
        if force:
            print("Deleting existing endpoint config")
            endpoint_config_delete(name=name, client=client)
        else:
            raise click.UsageError(
                "Must specify `force` if overwriting existing endpoint config")

    variants = [
        {
            'VariantName': model_name,
            'ModelName': model_name,
            'InitialInstanceCount': 1,
            'InstanceType': instance_type,
            # 'InitialVariantWeight': ...,
            # 'AcceleratorType': 'ml.eia1.medium'|'ml.eia1.large'|'ml.eia1.xlarge'|'ml.eia2.medium'|'ml.eia2.large'|'ml.eia2.xlarge'
        }
        for model_name in model]
    response = client.create_endpoint_config(
        EndpointConfigName=name,
        ProductionVariants=variants
    )
    arn = response['EndpointConfigArn']
    print("Created endpoint configuration [{}]".format(arn))
    """
    DataCaptureConfig={
        'EnableCapture': True|False,
        'InitialSamplingPercentage': 123,
        'DestinationS3Uri': 'string',
        'KmsKeyId': 'string',
        'CaptureOptions': [
            {
                'CaptureMode': 'Input'|'Output'
            },
        ],
        'CaptureContentTypeHeader': {
            'CsvContentTypes': [
                'string',
            ],
            'JsonContentTypes': [
                'string',
            ]
        }
    },
    """
    # Tags=[
    #    {
    #        'Key': 'string',
    #        'Value': 'string'
    #    },
    # ],
    # KmsKeyId='string'
    # print(response)


if __name__ == '__main__':
    session = sagemaker.Session()
    client = session.boto_session.client('sagemaker')
    description = endpoint_config_describe_run(
        client=client, name='mnist-demo-2020-10-06-04-32-42-393')
    print(description)
