from ..args import PathArgument, convert_path_arguments


class SageMakerProcessingConfig(object):
    def __init__(self, dependencies=None, inputs=None, outputs=None):
        self.dependencies = dependencies or {}
        self.inputs =  convert_path_arguments(inputs)
        self.outputs =  convert_path_arguments(outputs)
