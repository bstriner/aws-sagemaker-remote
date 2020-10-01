from ..modules import module_path


class SageMakerTrainingConfig(object):
    def __init__(self, inputs=None, dependencies=None):
        self.inputs = inputs or {}
        self.dependencies = dependencies or {}
        self.dependencies = {k: module_path(v)
                             for k, v in self.dependencies.items()}
