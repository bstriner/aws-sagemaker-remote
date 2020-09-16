
from sagemaker.session import Session as SagemakerSession
from boto3.session import Session as Boto3Session


def sagemaker_session(profile_name=None):
    if profile_name and len(profile_name) > 0:
        profile_name = profile_name
    else:
        profile_name = None
    boto_session = Boto3Session(profile_name=profile_name)
    sagemaker_session = SagemakerSession(boto_session=boto_session)
    return sagemaker_session
