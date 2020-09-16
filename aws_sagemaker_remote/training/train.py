from ..session import sagemaker_session
from .config import SageMakerTrainingConfig
import os
from sagemaker.pytorch import PyTorch


def sagemaker_training_run(
    script,
    args,
    config: SageMakerTrainingConfig,
    source=None,
    metrics=None
):
    if metrics is None:
        metrics = {}
    session = sagemaker_session(
        profile_name=args.sagemaker_profile
    )
    script = os.path.abspath(script)
    if source is None:
        source = os.path.dirname(script)
    if not script.startswith(source):
        raise ValueError("script=[{}] must be in source=[{}]")
    entry_point = script[len(source)+1:]
    metric_definitions = [
        {'Name': k, 'Regex': v}
        for k, v in metrics.items()
    ]

    estimator = PyTorch(
        sagemaker_session=session,
        base_job_name=args.sagemaker_job_name,
        entry_point=entry_point,
        source_dir=source,
        role=args.sagemaker_training_role,
        instance_type=args.sagemaker_training_instance,
        image_uri=args.sagemaker_training_image,
        instance_count=1,
        framework_version='1.5.0',
        # hyperparameters=hyperparameters_from_argparse(vars(args)),
        metric_definitions=metric_definitions
    )
    estimator.fit(config.channels)
    return estimator
