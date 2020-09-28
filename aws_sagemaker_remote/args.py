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
                raise ValueError("Unknown scheme or path does not exist: [{}]".format(path))
        except:
            pass
        return None

class PathArgument(object):
    def __init__(
        self,
        local=None,
        remote='default',
        optional=False,
        mode=None
    ):
        self.local = local
        self.remote = remote or 'default'
        self.optional = optional
        self.mode = mode
        if self.mode:
            assert self.mode in ['Pipe', 'File','EndOfJob', 'Continuous']
        #if self.optional and self.local:
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
