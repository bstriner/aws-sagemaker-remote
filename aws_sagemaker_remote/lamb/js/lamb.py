import subprocess
import tempfile
import os
import shutil
import boto3
import sagemaker
from aws_sagemaker_remote.util.cloudformation import get_cloudformation_output, stack_ready
from aws_sagemaker_remote.lamb.sam import sam_build, sam_deploy
import sys
import json

WEBPACK_CONFIG = os.path.abspath(os.path.join(
    __file__, '../webpack.config.js'
))
TEMPLATE_JS = os.path.abspath(os.path.join(
    __file__, '../template.yaml'
))
WEBPACK_PATH = os.path.abspath(os.path.join(
    __file__, '..'
))
BUILD_PACKAGE = os.path.abspath(os.path.join(
    __file__, '../build-package.json'
))


def ensure_lambda_js(
        path, stack_name, session,
        webpack=True, deploy=False, development=False,
        extra_files=None, package_json=None):
    cloudformation = session.client('cloudformation')
    if deploy or not stack_ready(cloudformation, stack_name):
        build_lambda_js(
            path, stack_name, session, webpack=webpack,
            extra_files=extra_files, package_json=package_json)


def build_lambda_js(
        path, stack_name, session, webpack=True, development=False,
        extra_files=None, package_json=None):
    sagemaker_session = sagemaker.Session(boto_session=session)
    bucket = sagemaker_session.default_bucket()
    bucket_arn = f"arn:aws:s3:::{bucket}"
    profile = session.profile_name
    #key = f"aws-sagemaker-remote/batch/{stack_name}"
    path = os.path.abspath(path)
    yarn = shutil.which('yarn')
    npx = shutil.which('npx')
    with tempfile.TemporaryDirectory() as tmp:
        try:
            pack_dir = os.path.join(tmp, 'pack')
            build_dir = os.path.join(tmp, 'build')
            # Install packages
            subprocess.check_output(
                [
                    yarn
                ],
                stderr=subprocess.STDOUT,
                cwd=path
            ).strip()
            if webpack:
                # Install webpack
                subprocess.check_output(
                    [
                        yarn
                    ],
                    stderr=subprocess.STDOUT,
                    cwd=WEBPACK_PATH
                ).strip()
                # Run webpack
                webpack_env = os.environ.copy()
                webpack_env['INPUT_DIR'] = path
                webpack_env['OUTPUT_DIR'] = pack_dir
                cmd = [
                    npx,
                    'webpack',
                    '--config',
                    WEBPACK_CONFIG,
                    '--mode',
                    ('development' if development else 'production')
                ]
                package_config = os.path.join(path, 'webpack.config.js')
                if os.path.exists(package_config):
                    cmd.extend([
                        '--merge',
                        '--config',
                        package_config
                    ])
                try:
                    subprocess.check_output(
                        cmd,
                        stderr=sys.stderr,
                        cwd=WEBPACK_PATH,
                        env=webpack_env
                    )
                except Exception as e:
                    cmd = " ".join(cmd)
                    print(
                        f"Failed to run command [{cmd}] in cwd [{WEBPACK_PATH}] from {path} to {pack_dir}")
                    raise e
                with open(BUILD_PACKAGE) as f:
                    package = json.load(f)
                    if package_json:
                        package.update(package_json)
                with open(os.path.join(pack_dir, 'package.json'), 'w') as f:
                    json.dump(package, f)
            else:
                shutil.copytree(
                    path,
                    pack_dir
                )

            # SAM build
            sam_build(
                build_dir=build_dir,
                base_dir=tmp,
                template_file=TEMPLATE_JS
            )
            if extra_files:
                for k, v in extra_files.items():
                    assert os.path.exists(os.path.join(
                        build_dir, 'LambdaFunction'
                    ))
                    target_path = os.path.join(build_dir, 'LambdaFunction', v)
                    if os.path.exists(
                        target_path
                    ):
                        os.remove(target_path)
                    source_path = k
                    if not os.path.exists(source_path):
                        other_path = os.path.join(
                            path,
                            k
                        )
                        if os.path.exists(
                            other_path
                        ):
                            source_path = other_path
                    if os.path.exists(source_path):
                        os.makedirs(
                            os.path.dirname(target_path),
                            exist_ok=True
                        )
                        shutil.copyfile(
                            source_path,
                            target_path
                        )
                    else:
                        raise ValueError(f"File {source_path} does not exist")
        except Exception as e:
            print(e)
            if sys.stdin.isatty():
                print(f"Temporary data in {tmp}")
                input("Press enter to continue...")
            raise e
        # SAM deploy
        sam_deploy(
            stack_name=stack_name,
            build_dir=build_dir,
            bucket=bucket,
            profile=profile,
            parameters={
                "BucketArn": bucket_arn
            }
        )


if __name__ == '__main__':
    from aws_sagemaker_remote.lamb.lamb import get_cloudformation_output
    profile = 'default'
    stack_name = 'demo-batch-js'
    path = 'demo/demo_batch/js'
    session = boto3.Session(profile_name=profile)
    cloudformation = session.client('cloudformation')
    build_lambda_js(
        path=path,
        stack_name=stack_name,
        session=session
    )
    arn = get_cloudformation_output(
        stack_name=stack_name,
        cloudformation=cloudformation,
        output_key='LambdaFunction'
    )
    print(arn)
