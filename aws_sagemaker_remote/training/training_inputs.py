from aws_sagemaker_remote.util.json_read import json_converter
from sagemaker.inputs import TrainingInput
from ..args import get_mode, get_s3_data_type, get_record_wrapping
from sagemaker.inputs import ShuffleConfig


def build_training_inputs(channels, args):
    return {
        k: build_training_input(channel=v, i=i, args=args) for i, (k, v) in enumerate(channels.items())
    }


def build_training_input(channel, i, args):
    attributes = channel.attributes
    if callable(attributes):
        attributes = attributes(args)
    return TrainingInput(
        s3_data=channel.local,
        # distribution=None,
        # compression=None,
        # content_type=None,
        record_wrapping=get_record_wrapping(channel.mode),
        # content_type='application/x-recordio' if get_mode(
        #        mode) not in ['File'] else None,
        s3_data_type=get_s3_data_type(channel.mode),
        input_mode=get_mode(channel.mode),
        attribute_names=attributes,
        shuffle_config=ShuffleConfig(123+i) if channel.shuffle else None
        # target_attribute_name=None,
        # shuffle_config=None,
    )
