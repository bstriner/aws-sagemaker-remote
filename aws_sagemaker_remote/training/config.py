class SageMakerTrainingConfig(object):
    def __init__(self, inputs=None, dependencies=None):
        self.inputs = inputs or {}
        self.dependencies = dependencies or {}
