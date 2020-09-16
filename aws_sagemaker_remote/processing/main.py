from .process import sagemaker_processing_run, sagemaker_processing_args
from argparse import ArgumentParser


def sagemaker_processing_main(
        script, main,
        **processing_args):
    parser = ArgumentParser()
    config = sagemaker_processing_args(parser=parser, **processing_args)
    args = parser.parse_args()
    if args.sagemaker_run:
        # Remote processing
        sagemaker_processing_run(
            args=args,
            config=config,
            script=script
        )
    else:
        # Local processing
        main(args)
