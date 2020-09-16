import argparse
import os
import pprint
from torch import nn
from torch.utils import data
from torchvision.datasets import MNIST
import torchvision.transforms as transforms
from aws_sagemaker_remote.processing import sagemaker_processing_main


def main(args):
    # Main function runs locally or remotely
    dataroot = args.output
    MNIST(
        root=dataroot, download=True, train=True,
        transform=transforms.ToTensor()
    )
    MNIST(
        root=dataroot, download=True, train=False,
        transform=transforms.ToTensor()
    )
    print("Downloaded MNIST")


if __name__ == '__main__':
    sagemaker_processing_main(
        script=__file__, # script path for remote execution
        main=main, # main function for local execution
        outputs={
            # Add the command line flag `output`
            # flag: (local default, s3 default)
            'output': ('output/data', 'default')
        },
        modules={
            # Add a module to SageMaker
            # module name: module path
            'aws_sagemaker_remote': os.path.join(__file__, '../..')
        },
        # Name the job
        job_name='demo-mnist-processor'
    )
