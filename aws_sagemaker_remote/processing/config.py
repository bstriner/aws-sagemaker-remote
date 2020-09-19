class SageMakerProcessingConfig(object):
    def __init__(self, dependencies=None, inputs=None, outputs=None):
        self.dependencies = dependencies or {}
        self.inputs = inputs or {}
        self.outputs = outputs or {}
