import re
import os
import argparse
import json
import shutil
from aws_sagemaker_remote.modules import module_path
from aws_sagemaker_remote.training.main import TrainingCommand
import aws_sagemaker_remote.util.copyxattr_patch  # patch for WSL
from aws_sagemaker_remote.util.fs import copy_file_or_dir


class ExportModelSpec(object):
    def __init__(
            self,
            #requirements=None,
            dependencies=None,
            args=None
    ):
        #self.requirements = requirements
        self.dependencies = dependencies or []
        if isinstance(args, argparse.Namespace):
            args = vars(args)
        self.args = args


def export_model_spec(model_dir, spec: ExportModelSpec):
    os.makedirs(model_dir, exist_ok=True)
    if spec.args:
        with open(os.path.join(model_dir, 'args.json'), 'w') as f:
            json.dump(spec.args, f)
    code_dir = os.path.join(model_dir, 'code')
    os.makedirs(code_dir, exist_ok=True)
    if spec.dependencies:
        dependencies = spec.dependencies
        if isinstance(dependencies, list):
            dependencies = {
                os.path.basename(module_path(k)): k for k in dependencies
            }
        for k, dep in spec.dependencies.items():
            dep = module_path(dep)
            des = os.path.join(
                model_dir, k
            )
            copy_file_or_dir(
                dep,
                des,
                file_subfolder=False
            )
    #if spec.requirements:
    #    shutil.copyfile(spec.requirements, os.path.join(
    #        code_dir, 'requirements.txt'
    #    ))


class ExportModelCommand(TrainingCommand):
    def build_spec(self, args):
        """
        return ExportModelSpec(
            requirements=args.requirements,    
            args=args
        )

        todo: add args to control spec
        """
        return self.spec

    def main(self, args):
        spec = self.build_spec(args)
        export_model_spec(
            spec=spec,
            model_dir=args.model_dir
        )

    def __init__(self, spec, help="Export package", **kwargs):
        self.spec = spec
        super().__init__(
            main=self.main,
            help=help,
            **kwargs
        )
        #self.inference_package_spec = inference_package_spec
