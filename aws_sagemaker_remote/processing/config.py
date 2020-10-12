from ..args import PathArgument, convert_path_arguments
from ..modules import module_path


class SageMakerProcessingConfig(object):
    def __init__(self, dependencies=None, inputs=None, outputs=None, env=None):
        self.inputs = convert_path_arguments(inputs)
        self.outputs = convert_path_arguments(outputs)
        self.dependencies = dependencies or {}
        self.dependencies = {
            k: module_path(v)
            for k, v in self.dependencies.items()
        }
        self.env = env or {}
