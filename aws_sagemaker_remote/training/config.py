from ..modules import module_path
from ..args import PathArgument, convert_path_arguments


class SageMakerTrainingConfig(object):
    def __init__(self, inputs=None, dependencies=None, env=None):
        self.inputs = convert_path_arguments(inputs)
        #print("SageMakerTrainingConfig inputs {}".format(self.inputs))
        self.dependencies = dependencies or {}
        self.dependencies = {k: module_path(v)
                             for k, v in self.dependencies.items()}
        self.env=env or {}
