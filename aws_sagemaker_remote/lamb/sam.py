import subprocess
import shutil

import sys


def parameter_overrides(parameters):
    if parameters:
        return [f"{k}={v}" for k, v in parameters.items()]
    else:
        return None


def sam_build(
    build_dir,
    base_dir,
    template_file,
    manifest=None,
    config_file=None,
    parameters=None,
    profile=None,
    region=None
):
    #sam = shutil.which('sam')
    # if sam:
    #    cmd = [sam]
    # else:
    #    cmd = [sys.executable, '-m','samcli']
    #raise ValueError("Program `sam` not found. Install `aws-sam-cli`")
    #print("build_dir: {}".format(build_dir))
    #print("base_dir: {}".format(base_dir))
    #print("template_file: {}".format(template_file))
    cmd = [
        sys.executable,
        '-m',
        'samcli',
        "build",
        "--build-dir",
        build_dir,
        "--base-dir",
        base_dir,
        "--template-file",
        template_file
    ]
    if manifest:
        cmd.extend([
            '--manifest',
            manifest
        ])
    if config_file:
        cmd.extend([
            "--config-file",
            config_file
        ])
    if profile:
        cmd.extend([
            '--profile',
            profile
        ])
    if region:
        cmd.extend([
            '--region', region
        ])
    parameters = parameter_overrides(parameters)
    if parameters:
        cmd.extend([
            '--parameter-overrides',
            *parameters
        ])
    #print(" ".join(cmd))
    try:
        subprocess.run(
            cmd,
            stderr=subprocess.STDOUT,
            cwd=base_dir,
            check=True
        )
    except Exception as e:
        print("Exception with command [{}]".format(" ".join(cmd)))
        print("Run in cwd [{}]".format(base_dir))
        print("Ensure package `aws-sam-cli` is installed correctly")
        raise e

def sam_deploy(
    build_dir,
    stack_name,
    bucket,
    # template_file,
    # manifest=None,
    # config_file=None,
    parameters=None,
    profile=None,
    region=None
):
    cmd = [
        sys.executable,
        '-m',
        'samcli',
        "deploy",
        "--no-fail-on-empty-changeset",
        "--capabilities",
        "CAPABILITY_IAM",
        '--stack-name',
        stack_name,
        '--s3-bucket',
        bucket
        # '--template-file',
        # template_file
    ]
    if region:
        cmd.extend([
            '--region', region
        ])
    if profile:
        cmd.extend([
            '--profile', profile
        ])
    parameters = parameter_overrides(parameters)
    if parameters:
        cmd.extend([
            '--parameter-overrides',
            *parameters
        ])
    #print(" ".join(cmd))
    
    try:
        subprocess.check_output(
            cmd,
            stderr=sys.stderr,
            cwd=build_dir
        )
    except Exception as e:
        print("Exception with command [{}]".format(" ".join(cmd)))
        print("Run in cwd [{}]".format(build_dir))
        print("Ensure package `aws-sam-cli` is installed correctly")
        raise e
