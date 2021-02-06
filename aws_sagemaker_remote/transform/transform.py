import boto3
import sagemaker
from click import UsageError
from sagemaker.utils import name_from_base


def transform_create(
    session: boto3.Session,
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
    payload_mb
):
    if(isinstance(session, sagemaker.Session)):
        session = session.boto_session
    if not job_name:
        if not base_job_name:
            raise UsageError(
                "Either --job-name or --base-job-name is required")
        job_name = name_from_base(base_job_name)
    print(f"Job name: {job_name}")
    client = session.client('sagemaker')
    response = client.create_transform_job(
        TransformJobName=job_name,
        ModelName=model_name,
        MaxConcurrentTransforms=concurrency,
        ModelClientConfig={
            'InvocationsTimeoutInSeconds': timeout,
            'InvocationsMaxRetries': retries
        },
        MaxPayloadInMB=payload_mb,
        BatchStrategy='SingleRecord',  # 'MultiRecord'|'SingleRecord',
        # Environment={
        #    'string': 'string'
        # },
        TransformInput={
            'DataSource': {
                'S3DataSource': {
                    'S3DataType': 'S3Prefix',  # 'ManifestFile'|'S3Prefix'|'AugmentedManifestFile',
                    'S3Uri': input_s3
                }
            },
            'ContentType': input_type,
            'CompressionType': 'None',  # |'Gzip',
            'SplitType': 'None'  # |'Line'|'RecordIO'|'TFRecord'
        },
        TransformOutput={
            'S3OutputPath': output_s3,  # 'string',
            'Accept': output_type,  # 'string',
            'AssembleWith': 'None'  # |'Line',
            # 'KmsKeyId': 'string'
        },
        TransformResources={
            'InstanceType': instance_type,  # 'ml.m4.xlarge'|'ml.m4.2xlarge'|'ml.m4.4xlarge'|'ml.m4.10xlarge'|'ml.m4.16xlarge'|'ml.c4.xlarge'|'ml.c4.2xlarge'|'ml.c4.4xlarge'|'ml.c4.8xlarge'|'ml.p2.xlarge'|'ml.p2.8xlarge'|'ml.p2.16xlarge'|'ml.p3.2xlarge'|'ml.p3.8xlarge'|'ml.p3.16xlarge'|'ml.c5.xlarge'|'ml.c5.2xlarge'|'ml.c5.4xlarge'|'ml.c5.9xlarge'|'ml.c5.18xlarge'|'ml.m5.large'|'ml.m5.xlarge'|'ml.m5.2xlarge'|'ml.m5.4xlarge'|'ml.m5.12xlarge'|'ml.m5.24xlarge',
            'InstanceCount': instance_count,
            # 'VolumeKmsKeyId': 'string'
        },
        # DataProcessing={
        #    'InputFilter': 'string',
        #    'OutputFilter': 'string',
        #    'JoinSource': 'Input'|'None'
        # },
        Tags=[
            {
                'Key': 'Source',
                'Value': 'aws-sagemaker-remote'
            },
        ],
        # ExperimentConfig={
        #    'ExperimentName': 'string',
        #    'TrialName': 'string',
        #    'TrialComponentDisplayName': 'string'
        # }
    )
    print(f"Response: {response}")
    arn = response.get('TransformJobArn', None)
    print(f"ARN: {arn}")
