import sagemaker
import boto3
import pprint
from aws_sagemaker_remote.util.fields import get_field


def processing_describe(job_name, session, field=None):
    if isinstance(session, sagemaker.Session):
        session = session.boto_session
    client = session.client('sagemaker')
    description = processing_describe_get(job_name=job_name, client=client)
    description = get_field(description, field)
    return description


def processing_describe_get(client, job_name):
    description = client.describe_processing_job(
        ProcessingJobName=job_name
    )
    return description


if __name__ == '__main__':
    session = sagemaker.Session(
        boto_session=boto3.Session(profile_name='default'))
    description = processing_describe(
        session=session, job_name='voxceleb-convert-vox2test-2020-10-07-09-23-16-900')
    print(description)
