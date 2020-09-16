import argparse
from distutils.util import strtobool
import os

PROFILE = 'default'


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
