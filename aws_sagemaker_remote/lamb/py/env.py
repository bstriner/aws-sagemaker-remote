
import boto3
import tempfile
import os
import shutil
import re
from venv import EnvBuilder
import subprocess


def lambda_create_python(name, code):
    # with tempfile.TemporaryDirectory() as tmp:
    tmp = 'output/tmp'
    os.makedirs(tmp, exist_ok=True)
    build_path = os.path.join(tmp, 'build')
    # os.makedirs(build_path)
    copy_contents(code, build_path, ignore=lambda_ignore)
    requirements = os.path.join(build_path, 'requirements.txt')
    if not os.path.exists(requirements):
        requirements = None
    env_path = os.path.join(tmp, 'venv')
    #if not os.path.exists(env_path):
    builder = LambdaEnvBuilder(
        requirements=requirements,
        with_pip=True
    )
    builder.create(env_path)
    print(builder.saved_context)
    print(dir(builder.saved_context))
    print(builder.saved_packages)


class LambdaEnvBuilder(EnvBuilder):
    def __init__(self, *args, requirements=None, **kwargs):
        super(LambdaEnvBuilder, self).__init__(*args, **kwargs)
        self.requirements = requirements
        self.saved_context = None
        self.saved_packages = None

    def post_setup(self, context):
        if self.requirements:
            cmd = [
                context.env_exe, '-m', 'pip',
                'install', '-r', self.requirements
            ]
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        cmd = [
            context.env_exe, '-c', 'import site;print(site.getusersitepackages())'
        ]
        self.saved_packages = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT).strip()
        self.saved_context = context
        print("Context: {}".format(context))

