import argparse
import os
import pprint
from torch import nn
from torch.utils import data
from torchvision.datasets import MNIST
import torchvision.transforms as transforms
from aws_sagemaker_remote.training import sagemaker_training_main
import aws_sagemaker_remote


def show_path(path):
    if path.startswith('s3://'):
        print("Path [{}] is on s3".format(path))
    else:
        if os.path.exists(path):
            print("Path [{}] exists".format(path))
            if os.path.isdir(path):
                print("Directory contents: {}".format(
                    list(os.listdir(path))
                ))
            elif os.path.isfile(path):
                with open(path) as f:
                    contents = f.read()
                print("File contents: [{}]".format(contents))
            else:
                print("Path [{}] is not file or folder".format(path))
        else:
            print("Path [{}] does not exist".format(path))


def main(args):
    # Main function runs locally or remotely
    print("Test folder: {}".format(args.test_folder))
    show_path(args.test_folder)
    print("Test file: {}".format(args.test_file))
    show_path(args.test_file)
    print("Test S3 folder: {}".format(args.test_s3_folder))
    show_path(args.test_s3_folder)
    print("Test S3 file: {}".format(args.test_s3_file))
    show_path(args.test_s3_file)


if __name__ == '__main__':
    sagemaker_training_main(
        main=main,  # main function for local execution
        inputs={
            'test_folder': 'demo/test_folder',
            'test_file': 'demo/test_folder/test_file.txt',
            'test_s3_folder': 's3://sagemaker-us-east-1-683880991063/test_folder',
            'test_s3_file': 's3://sagemaker-us-east-1-683880991063/test_folder/test_file.txt'
        },
        dependencies={
            # Add a module to SageMaker
            # module name: module path
            'aws_sagemaker_remote': aws_sagemaker_remote
        },
        #configuration_command='pip3 install --upgrade sagemaker sagemaker-experiments',
        # Name the job
        base_job_name='demo-training-inputs'
    )
