import re
import os
import argparse
import json
import shutil
from aws_sagemaker_remote.modules import module_path
from aws_sagemaker_remote.training.main import TrainingCommand
import aws_sagemaker_remote.util.copyxattr_patch


class InferencePackageSpec(object):
    def __init__(self,
                 requirements=None,
                 dependencies=None,
                 args=None):
        self.requirements = requirements
        self.dependencies = dependencies or []
        if isinstance(args, argparse.Namespace):
            args = vars(args)
        self.args = args


def python_ignore(path, names):
    return [
        name for name in names
        if re.match("__pycache__|\\.git", name)
    ]


def export_package(model_dir, inference_spec: InferencePackageSpec):
    os.makedirs(model_dir, exist_ok=True)
    if inference_spec.args:
        with open(os.path.join(model_dir, 'args.json'), 'w') as f:
            json.dump(inference_spec.args, f)
    code_dir = os.path.join(model_dir, 'code')
    os.makedirs(code_dir, exist_ok=True)
    if inference_spec.dependencies:
        for dep in inference_spec.dependencies:
            dep = module_path(dep)
            des = os.path.join(
                code_dir, os.path.basename(dep)
            )
            if os.path.exists(des):
                if os.path.isdir(des):
                    shutil.rmtree(des)
                else:
                    os.remove(des)
            if os.path.isdir(dep):
                shutil.copytree(
                    dep,
                    des,
                    # dirs_exist_ok=True,
                    ignore=python_ignore
                )
            else:
                shutil.copyfile(
                    dep,
                    des
                )
    if inference_spec.requirements:
        shutil.copyfile(inference_spec.requirements, os.path.join(
            code_dir, 'requirements.txt'
        ))


class ExportModelCommand(TrainingCommand):
    def inference_spec(self, args):
        return InferencePackageSpec(args=args)

    def main(self, args):
        export_package(
            model_dir=args.model_dir,
            inference_spec=self.inference_spec(args)
        )

    def __init__(self, script=None, help=None, metrics=None, **training_args):
        super().__init__(
            main=self.main,
            script=script,
            help=help,
            metrics=metrics,
            **training_args
        )
        #self.inference_package_spec = inference_package_spec

    pass
