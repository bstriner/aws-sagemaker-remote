class SageMakerTrainingConfig(object):
    def __init__(self, channels=None):
        self.channels = channels or {}
        