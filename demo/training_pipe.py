import argparse
import os
import pprint
from torch import nn
from torch.utils import data
from torchvision.datasets import MNIST
import torchvision.transforms as transforms
from aws_sagemaker_remote.training import sagemaker_training_main
import aws_sagemaker_remote
from aws_sagemaker_remote.args import PathArgument
import stat
import pathlib
import glob
from scipy.io import wavfile
from io import BytesIO
from aws_sagemaker_remote.util.pipes import chunk_iterable
from sagemaker.amazon.record_pb2 import Record
from sagemaker.amazon.common import read_recordio


def read_pipe(pipe):
    for i in range(5):
        with open(pipe+"_{}".format(i), 'rb') as f:
            print("opened pipe {}".format(i))
            count = 0
            for label, f1, f2 in chunk_iterable(read_recordio(f), 3):
                label = int(label.decode('utf-8'))
                fs1, aud1 = wavfile.read(BytesIO(f1))
                fs2, aud2 = wavfile.read(BytesIO(f2))
                print("{} label: {}".format(count, label))
                print("audio1: {},{}".format(fs1, aud1.shape))
                print("audio2: {},{}".format(fs2, aud2.shape))
                count += 1


def main(args):
    # Main function runs locally or remotely
    print("Test folder: {}".format(args.test_pipe))
    if isinstance(args.test_pipe, dict):
        for k, v in args.test_pipe.items():
            print("Pipe dict entry {}->{}".format(k, v))
            print("Glob: {}".format(list(glob.glob(os.path.join(
                os.path.dirname(v), "**", "*"), recursive=True))))
            read_pipe(v)
    elif isinstance(args.test_pipe, str):
        print("Pipe {}".format(args.test_pipe))
        read_pipe(args.test_pipe)
    else:
        raise ValueError("Input should be string or dictionary")

    """
    show_path(args.test_pipe)
    print("Test S3 file pipe manifest: {}-manifest".format(args.test_pipe))
    show_path("{}-manifest".format(args.test_pipe))
    print("Input path: {}".format(os.path.dirname(args.test_pipe)))
    show_path(os.path.dirname(args.test_pipe))
    print("Test S3 file pipe 0: {}_0".format(args.test_pipe))
    read_pipe(args.test_pipe)
    """


if __name__ == '__main__':
    sagemaker_training_main(
        main=main,  # main function for local execution
        inputs={
            'test_pipe': PathArgument(
                'output/manifest-speakers/manifest-speakers',
                mode='AugmentedManifestFolder',
                attributes=['label', 'audio-1-ref', 'audio-2-ref']
            )
        },
        dependencies={
            # Add a module to SageMaker
            # module name: module path
            'aws_sagemaker_remote': aws_sagemaker_remote
        },
        #configuration_command='pip3 install --upgrade sagemaker sagemaker-experiments',
        # Name the job
        base_job_name='demo-training-pipe',
        volume_size=20
    )

"""
split-lines --input demo/test_folder/manifest-speakers.json --output output/manifest-speakers --splits 2 --size 2
aws s3 sync demo/test_folder s3://sagemaker-us-east-1-683880991063/test_folder
python demo\training_pipe.py --sagemaker-run yes --sagemaker-training-instance ml.m5.large
"""
