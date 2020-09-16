from .train import sagemaker_training_run
from .args import sagemaker_training_args
from argparse import ArgumentParser


def sagemaker_training_main(
        script, main, metrics=None, source=None,
        **training_args):
    parser = ArgumentParser()
    config = sagemaker_training_args(parser=parser, **training_args)
    args = parser.parse_args()
    if args.sagemaker_run:
        # Remote processing
        sagemaker_training_run(
            script=script,
            source=source,
            args=args,
            config=config,
            metrics=metrics)
    else:
        # Local processing
        main(args)
