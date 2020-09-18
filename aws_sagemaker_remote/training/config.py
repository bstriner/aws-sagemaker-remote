class SageMakerTrainingConfig(object):
    def __init__(self, channels=None, dependencies=None):
        self.channels = channels or {}
        self.dependencies = dependencies or {}
