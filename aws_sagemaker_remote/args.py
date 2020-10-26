import argparse
from distutils.util import strtobool
import os
from urllib.parse import urlparse
from urllib.request import url2pathname

PROFILE = 'default'


def get_local_path(path):
    if not path:
        return None
    elif os.path.exists(path):
        return os.path.abspath(path)
    else:
        try:
            url = urlparse(path)
            if url.scheme in ['file', '']:
                path = url2pathname(url.path)
                return os.path.abspath(path)
            elif url.scheme in ['s3']:
                return None
            else:
                raise ValueError(
                    "Unknown scheme or path does not exist: [{}]".format(path))
        except:
            pass
        return None


def get_mode(mode):
    if not mode:
        return 'File'
    elif mode in [
        'Pipe',
        'ManifestFile',
        'AugmentedManifestFile',
        'ManifestFolder',
        'AugmentedManifestFolder'
    ]:
        return 'Pipe'
    elif mode in ['File', 'EndOfJob', 'Continuous']:
        return mode
    else:
        raise ValueError("Unknown mode: {}".format(mode))


def get_s3_data_type(mode):
    if not mode:
        return 'S3Prefix'
    elif mode == 'ManifestFile':
        return 'ManifestFile'
    elif mode == 'AugmentedManifestFile':
        return 'AugmentedManifestFile'
    elif mode == 'ManifestFolder':
        return 'ManifestFile'
    elif mode == 'AugmentedManifestFolder':
        return 'AugmentedManifestFile'
    elif mode in ['File', 'EndOfJob', 'Continuous', 'Pipe']:
        return 'S3Prefix'
    else:
        raise ValueError("Unknown mode: {}".format(mode))


class PathArgument(object):
    def __init__(
        self,
        local=None,
        remote='default',
        optional=False,
        mode=None,
        attributes=None,
        split_workers='workers',
        split_batch_size='batch_size',
    ):
        self.local = local
        self.remote = remote or 'default'
        self.optional = optional
        self.mode = mode
        self.attributes = attributes
        self.split_workers = split_workers
        self.split_batch_size = split_batch_size
        if self.mode:
            assert self.mode in [
                'Pipe', 'ManifestFile', 'AugmentedManifestFile',
                'ManifestFolder', 'AugmentedManifestFolder',
                'File', 'EndOfJob', 'Continuous'
            ]
        # if self.optional and self.local:
        #    print("Optional inputs must default to nothing")


OPTIONAL = PathArgument(optional=True)


def convert_path_argument(param, cls=PathArgument):
    if isinstance(param, cls):
        return param
    elif isinstance(param, str):
        return cls(param)
    else:
        raise ValueError(
            "Unexpected path type [{}]: [{}]".format(type(param), param))


def convert_path_arguments(params, cls=PathArgument):
    if params:
        return {
            k: convert_path_argument(v, cls=cls) for k, v in params.items()
        }
    else:
        return {}


def variable_to_argparse(variable):
    return "--{}".format(variable.replace("_", "-"))


def argparse_to_variable(flag):
    assert flag.startswith('--')
    return flag[2:].replace('-', '_')


def strtobool_type(v):
    return bool(strtobool(v))


def bool_argument(
    parser: argparse.ArgumentParser,
    *args,
    **kwargs
):
    parser.add_argument(*args, **kwargs, type=strtobool_type,
                        const=True, nargs="?")


def sagemaker_profile_args(parser, profile=PROFILE):
    parser.add_argument('--sagemaker-profile', default=profile,
                        help='AWS profile for SageMaker session (default: [{}])'.format(profile))
