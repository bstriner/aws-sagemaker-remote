import os
import docker
import base64


class Image(object):
    def __init__(self, name, path, tag, accounts=[]):
        self.name = name
        self.path = path
        self.tag = tag
        self.accounts = accounts


class Images(object):
    INFERENCE = Image(
        'inference',
        os.path.abspath(os.path.join(__file__, '../inference')),
        'aws-sagemaker-remote-inference:latest',
        ['763104351884']
    )

    PROCESSING = Image(
        'processing',
        os.path.abspath(os.path.join(__file__, '../processing')),
        'aws-sagemaker-remote-processing:latest',
        ['763104351884']
    )

    TRAINING = Image(
        'training',
        os.path.abspath(os.path.join(__file__, '../training')),
        'aws-sagemaker-remote-training:latest',
        ['763104351884']
    )

    ALL = [
        INFERENCE,
        PROCESSING,
        TRAINING
    ]

# Repository management


def ecr_repository_exists(ecr, account, name):
    return ecr_describe_repository(ecr, account, name) is not None


def ecr_describe_repository(ecr, account, name):
    try:
        response = ecr.describe_repositories(
            registryId=account,
            repositoryNames=[
                name,
            ]
        )
    except Exception:
        return None
    repo = response['repositories']
    if len(repo) > 0:
        return repo[0]
    else:
        return None


def ecr_create_repository(ecr, name):
    repo = ecr.create_repository(
        repositoryName=name,
        tags=[
            {
                'Key': 'Source',
                'Value': 'aws-sagemaker-remote'
            },
            # todo: add metadata
        ],
        imageTagMutability='MUTABLE',
        imageScanningConfiguration={
            'scanOnPush': False
        },
        #    encryptionConfiguration={
        #        'encryptionType': 'AES256'|'KMS',
        #        'kmsKey': 'string'
        #    }
    )
    #print("create repo {}".format(repo))
    repo = repo['repository']
    print("Created ECR repository {}".format(name))
    return repo


def ecr_ensure_repo(ecr, account, name, user_account):
    repo = ecr_describe_repository(ecr, account, name)
    if repo is not None:
        return repo
    if account != user_account:
        # todo: check on external accounts
        raise ValueError(
            "Repository {}/{} does not exist and cannot be created because it is in account {} and you are in account {}",
            account, name, account, user_account
        )
    return ecr_create_repository(ecr, name)


def ecr_login(ecr, docker_client, accounts):
    accounts = [account for account in accounts if account]
    token = ecr.get_authorization_token(registryIds=accounts)
    for auth_data in token['authorizationData']:
        username, password = base64.b64decode(
            auth_data['authorizationToken']
        ).decode().split(':')
        registry = auth_data['proxyEndpoint']
        # login =
        docker_client.login(
            username, password, registry=registry, reauth=True)
        print("Logged in to ECR {}".format(registry))
        #print("un/pw: {}:{}, reg: {}, login: {}".format(username, password, registry, login))

# Image operations


def ecr_ensure_image(
    path, tag, accounts, session
):
    ecr = session.client('ecr')  # , region_name='eu-west-1')
    user_account = get_account(session)
    tag_account, tag_repo, tag_tag = parse_image(tag, account=user_account)
    img = get_image(ecr, tag_account, tag_repo, tag_tag)
    if img is not None:
        repo = ecr_ensure_repo(ecr, tag_account, tag_repo, user_account)
        repo_uri = repo['repositoryUri']
        full_uri = "{}:{}".format(repo_uri, tag_tag)
        return full_uri
    else:
        return ecr_build_image(
            path=path,
            tag=tag,
            accounts=accounts,
            session=session,
            pull=False,
            cache=True
        )


def ecr_build_image(
    path, tag, accounts, cache, pull, session
):
    # todo: add region param
    ecr = session.client('ecr')  # , region_name='eu-west-1')
    region_name = session.region_name
    if not region_name:
        raise ValueError("No default region name in your AWS profile")
    user_account = get_account(session)
    tag_account, tag_repo, tag_tag = parse_image(tag, account=user_account)
    repo = ecr_ensure_repo(ecr, tag_account, tag_repo, user_account)
    repo_uri = repo['repositoryUri']

    if not accounts:
        accounts = []
    if tag_account not in accounts:
        accounts = [tag_account] + list(accounts)
    client = docker.from_env()
    ecr_login(ecr, client, accounts)
    image_full = "{}:{}".format(repo_uri, tag_tag)
    print("Building image {}".format(image_full))
    client.images.build(
        path=path,
        tag=image_full,
        buildargs={
            "REGION": region_name
        },
        quiet=False,
        nocache=not cache,
        pull=pull
    )
    print("Built image {}".format(image_full))
    #repo = "{}.dkr.ecr.{}.amazonaws.com/"
    client.images.push(repo_uri, tag_tag)
    print("Pushed image {}".format(image_full))
    return image_full
    # 683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo:inference


def image_exists(ecr, registry, repository, tag):
    return get_image(ecr, registry, repository, tag) is not None


def get_image(ecr, registry, repository, tag):
    try:
        img = ecr.batch_get_image(
            registryId=registry,
            repositoryName=repository,
            imageIds=[
                {
                    'imageTag': tag
                }
            ]
        )
    except Exception:
        # todo: check for RepositoryNotFoundException
        return None
    img = img['images']
    if len(img) > 0:
        return img[0]
    else:
        return None


def get_account(session):
    return session.client('sts').get_caller_identity().get('Account')


def parse_image(uri, account):
    """
    TRAINING_IMAGE = '683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo-sagemaker-training:latest'
    """
    try:
        uri = uri.split("/")
        if len(uri) == 2:
            host, path = uri
            account = host.split(".")[0]
        elif len(uri) == 1:
            account = account
            path = uri[0]
        else:
            raise ValueError("Invalid uri")

        path = path.split(":")
        if len(path) == 2:
            name, tag = path
        elif len(path) == 1:
            name = path[0]
            tag = 'latest'
        else:
            raise "Invalid URI"
        return account, name, tag

    except Exception as e:
        raise ValueError("Invalid ECR URI: {}".format(uri)) from e


if __name__ == '__main__':
    """
    account = '683880991063'
    print(parse_image(
        '683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo-sagemaker-training:latest', account=account))
    print(parse_image(
        '683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo-sagemaker-training', account=account))
    print(parse_image('columbo-sagemaker-training:latest', account=account))
    print(parse_image('columbo-sagemaker-training', account=account))

    from boto3 import Session
    session = Session(profile_name='default')
    ecr = session.client('ecr')
    account = get_account(session)
    img = get_image(
        ecr, *parse_image('columbo-sagemaker-training', account=account))
    print(img)

    repo = ecr_describe_repository(ecr, account, 'columbo-sagemaker-training')
    print(repo)
    """
    from boto3 import Session
    session = Session(profile_name='default')
    ecr = session.client('ecr')
    account = get_account(session)
    for image in Images.ALL:
        img = ecr_ensure_image(
            path=image.path,
            tag=image.tag,
            accounts=image.accounts,
            session=session
        )
        print("Image: {}".format(img))
