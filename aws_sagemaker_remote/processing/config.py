class SageMakerProcessingConfig(object):
    def __init__(self, modules=None, inputs=None, outputs=None):
        self.modules = modules or {}
        self.inputs = inputs or {}
        self.outputs = outputs or {}
