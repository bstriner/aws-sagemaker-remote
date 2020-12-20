import sagemaker
import pprint
from aws_sagemaker_remote.util.fields import get_field
from aws_sagemaker_remote.util.sts import get_account


def batch_describe(job_id, session, field=None):
    if isinstance(session, sagemaker.Session):
        session = session.boto_session
    client = session.client('s3control')
    account_id = get_account(session)
    description = batch_describe_get(
        account_id=account_id,
        job_id=job_id,
        client=client)
    description = get_field(description, field)
    return description


def batch_describe_get(client, account_id, job_id):
    description = client.describe_job(
        AccountId=account_id,
        JobId=job_id
    )
    description = description.get('Job')
    return description


if __name__ == '__main__':
    import boto3
    session = sagemaker.Session(
        boto_session=boto3.Session(profile_name='default'))
    description = batch_describe(job_id='ee1e7233-2668-4320-9fff-e13613bd7622',
                                 session=session, field=None)
    print(description)

    description = batch_describe(job_id='ee1e7233-2668-4320-9fff-e13613bd7622',
                                 session=session, field="Report.s3")
    print(description)
