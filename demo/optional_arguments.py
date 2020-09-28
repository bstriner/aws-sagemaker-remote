import argparse
import os
import pprint
from torch import nn
from torch.utils import data
from torchvision.datasets import MNIST
import torchvision.transforms as transforms
from aws_sagemaker_remote.processing import sagemaker_processing_main
from aws_sagemaker_remote.args import OPTIONAL

def main(args):
    # Main function runs locally or remotely
    print("ARGS")
    print(vars(args))
    path = args.input
    print("Input: [{}]".format(path))
    if path:
        if os.path.exists(path):
            if os.path.isfile(path):
                print("Reading input file")
                with open(path) as f:
                    print(f.read())
            elif os.path.isdir(path):
                print("Is directory")
                print("Listing: {}".format(list(os.listdir(path))))
            else:
                raise ValueError("Neither file nor directory")
        else:
            print("Path does not exist")
    else:
        print("Path is empty")


if __name__ == '__main__':
    sagemaker_processing_main(
        main=main, # main function for local execution
        inputs={
            # Add the command line flag `output`
            # flag: (local default, s3 default)
            'input': OPTIONAL
        },
        dependencies={
            # Add a module to SageMaker
            # module name: module path
            'aws_sagemaker_remote': os.path.join(__file__, '../../aws_sagemaker_remote')
        },
        configuration_command='pip3 install --upgrade sagemaker sagemaker-experiments',
        # Name the job
        base_job_name='demo-optional-arguments'
    )
