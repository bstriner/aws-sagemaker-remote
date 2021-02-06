from aws_sagemaker_remote.batch.main import BatchCommand, BatchConfig
import os
import argparse
from demo_batch.demo_batch import command


def parser():
    # This function is only necessary to generate documentation
    return command().parser()
