from aws_sagemaker_remote.s3 import get_file_type, FileType, download_file_or_folder
import os
import base64
import warnings
from aws_sagemaker_remote.util.cli_argument import cli_argument
try:
    import docker
    from docker.errors import BuildError
except:
    warnings.warn(
        "Python `docker` package not installed. \
        Some aws-sagemaker-remote features may not be available"
    )
from aws_sagemaker_remote.util.sts import get_account


class Image(object):
    def __init__(self, path, tag, accounts=[], name=None, download_files=None):
        self.name = name
        self.path = path
        self.tag = tag
        self.accounts = accounts or []
        self.download_files = download_files or {}

    def __str__(self):
        accounts = ", ".join(self.accounts)
        return f"Image(name: {self.name}, path: {self.path}, tag: {self.tag})"


class Images(object):
    INFERENCE = Image(
        name='inference',
        path=os.path.abspath(os.path.join(__file__, '../inference')),
        tag='aws-sagemaker-remote-inference:latest',
        accounts=['763104351884']
    )

    PROCESSING = Image(
        name='processing',
        path=os.path.abspath(os.path.join(__file__, '../processing')),
        tag='aws-sagemaker-remote-processing:latest',
        accounts=['763104351884']
    )

    TRAINING = Image(
        name='training',
        path=os.path.abspath(os.path.join(__file__, '../training')),
        tag='aws-sagemaker-remote-training:latest',
        accounts=['763104351884']
    )

    TRAINING_GPU = Image(
        name='training:gpu',
        path=os.path.abspath(os.path.join(__file__, '../training')),
        tag='aws-sagemaker-remote-training:gpu',
        accounts=['763104351884']
    )

    ALL = [
        INFERENCE,
        PROCESSING,
        TRAINING,
        TRAINING_GPU
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
    print(f"Creating repository '{name}'")
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
        login = docker_client.login(
            username, password, registry=registry, reauth=True
        )
        status = ""
        if login and 'Status' in login:
            status = ": {}".format(login['Status'])
        print("Logged in to ECR {}{}".format(registry, status))
        #print("un/pw: {}:{}, reg: {}, login: {}".format(username, password, registry, login))

# Image operations


def ecr_ensure_image(
    image, session, force=False, cache=True, pull=True, push=True, wsl=False
):
    ecr = session.client('ecr')  # , region_name='eu-west-1')
    user_account = get_account(session)
    tag_account, tag_repo, tag_tag = parse_image(
        image.tag, account=user_account)
    if not force:
        img = get_image(ecr, tag_account, tag_repo, tag_tag)
        if img is not None:
            repo = ecr_ensure_repo(ecr, tag_account, tag_repo, user_account)
            repo_uri = repo['repositoryUri']
            full_uri = "{}:{}".format(repo_uri, tag_tag)
            return full_uri
    return ecr_build_image(
        image=image,
        session=session,
        pull=pull,
        cache=cache,
        push=push,
        wsl=wsl
    )


def download_files(
    files, session, base
):
    #print(f"download_files: {files} to base {base}")
    s3 = session.client('s3')
    ret = {}
    for k, v in files.items():
        dest = os.path.join(base, k)
        v = cli_argument(v, session=session)
        if os.path.exists(v):
            ret[k.upper()] = v
        elif os.path.exists(dest):
            ret[k.upper()] = dest
        elif v.startswith("s3://"):
            ret[k.upper()] = download_file_or_folder(
                uri=v,
                session=session,
                dest=dest,
                file_subfolder=True
            )
        else:
            raise ValueError(f"Unhandled file path {k}: {v}")
    #print(f"downloaded_files: {ret}")
    return ret


def ecr_build_image(
    image: Image, session, cache=True, pull=True, push=True,wsl=False
):
    print(f"Building image: {image}")
    # todo: add region param
    ecr = session.client('ecr')  # , region_name='eu-west-1')
    region_name = session.region_name
    if not region_name:
        raise ValueError("No default region name in your AWS profile")
    user_account = get_account(session)
    tag_account, tag_repo, tag_tag = parse_image(
        image.tag, account=user_account)
    repo = ecr_ensure_repo(ecr, tag_account, tag_repo, user_account)
    repo_uri = repo['repositoryUri']
    path = os.path.join(image.path, tag_tag)

    accounts = list(image.accounts)
    if tag_account not in accounts:
        accounts.append(tag_account)
    client = docker.from_env()
    ecr_login(ecr, client, accounts)
    image_full = "{}:{}".format(repo_uri, tag_tag)
    print("Building image {} (cache: {}, pull:{})".format(
        image_full,
        cache, pull
    ))
    buildargs = {
        "REGION": region_name,
        "ACCOUNT": tag_account
    }
    base_path = os.path.join(image.path, tag_tag)
    #base_path = image.path
    df = download_files(
            files=image.download_files,
            session=session,
            base=base_path  # todo: optional temp dir if write only
        )
    if wsl:
        tdf = {}
        for k,v in df.items():
            v = v.replace("\\","/")
            if v[1] == ":":
                v = f"/mnt/{v[0]}{v[2:]}"
            tdf[k]=v
        df=tdf
    buildargs.update(
        df
    )
    print(f"buildargs: {buildargs}")
    try:
        streamer = client.images.build(
            path=path,
            tag=image_full,
            buildargs=buildargs,
            quiet=False,
            nocache=not cache,
            pull=pull,
            #decode=True
        )
    except BuildError as e:
        for l in e.build_log:
            if 'stream' in l:
                for line in l['stream'].splitlines():
                    print(line)
        raise e
    """
    for chunk in streamer.build_log:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                print(line)
    """
    print("Built image {}".format(image_full))
    #repo = "{}.dkr.ecr.{}.amazonaws.com/"

    if push:
        print("Pushing image {}".format(image_full))
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


def parse_image(uri, account):
    """
    TRAINING_IMAGE = '683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo-sagemaker-training:latest'
    """
    print("parse_image: {}, account: {}".format(uri, account))
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
            image=image,
            session=session
        )
        print("Image: {}".format(img))
