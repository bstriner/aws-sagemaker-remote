import argparse
from aws_sagemaker_remote.processing.args import sagemaker_processing_input_args

from aws_sagemaker_remote.processing.args import sagemaker_processing_output_args

from aws_sagemaker_remote.args import convert_path_arguments

def test_processing_inputs():
    parser = argparse.ArgumentParser()
    sagemaker_processing_input_args(
        parser=parser,
        inputs=convert_path_arguments({
            'dataset1':'data/ds1',
            'dataset2':'data/ds2'
        })
    )
    args=parser.parse_args(args=['--dataset2','data/ds3'])
    assert args.dataset1 == 'data/ds1'
    assert args.dataset2 == 'data/ds3'

def test_processing_outputs():
    parser = argparse.ArgumentParser()
    sagemaker_processing_output_args(
        parser=parser,
        outputs=convert_path_arguments({
            'dataset1':'data/ds1',
            'dataset2':'data/ds2'
        })
    )
    args=parser.parse_args(args=['--dataset2','data/ds3'])
    assert args.dataset1 == 'data/ds1'
    assert args.dataset2 == 'data/ds3'
