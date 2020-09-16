from botocore.exceptions import ClientError
SAGEMAKER_FULL_ACCESS = 'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'


def is_boto_exception(e, code):
    return (
        hasattr(e, 'response')
        and 'Error' in e.response
        and 'Code' in e.response['Error']
        and e.response['Error']['Code'] == code
    )


def ensure_role(iam, role_name, description, policies, trust):
    role = get_role_by_name(iam, role_name=role_name)
    if role is None:
        role = create_role(iam=iam, role_name=role_name,
                           description=description, policies=policies, trust=trust)
    return role['Arn']


def get_role_by_name(iam, role_name):
    try:
        response = iam.get_role(
            RoleName=role_name
        )
        return response['Role']
    except ClientError as e:
        if is_boto_exception(e, 'NoSuchEntity'):
            return None
        else:
            raise e


def create_role(iam, role_name, description, policies, trust):
    print("Creating role [{}]".format(role_name))
    response = iam.create_role(
        # Path='string',
        RoleName=role_name,
        AssumeRolePolicyDocument=trust.strip(),
        Description=description,
        # MaxSessionDuration=123,
        # PermissionsBoundary='string',
        Tags=[
            {
                'Key': 'Source',
                'Value': 'aws-ecs-remote'
            },
        ]
    )
    role = response['Role']
    for policy in policies:
        response = iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy
        )
    return role
