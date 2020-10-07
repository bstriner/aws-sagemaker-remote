from botocore.exceptions import ClientError
from ..iam import SAGEMAKER_FULL_ACCESS, ensure_role

INFERENCE_ROLE = {
    'description': 'Role for SageMaker inference (aws-sagemaker-remote)',
    'policies': [SAGEMAKER_FULL_ACCESS],
    'trust': """
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "sagemaker.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"""
}


def ensure_inference_role(iam, role_name):
    return ensure_role(iam=iam, role_name=role_name, **INFERENCE_ROLE)
