from .train import sagemaker_training_run
from .args import sagemaker_training_args, sagemaker_env_args
from argparse import ArgumentParser
import inspect
import os
import warnings
import types
from ..commands import Command, run_command


def sagemaker_training_handle(args, config, main, metrics=None):
    if args.sagemaker_run:
        # Remote processing
        sagemaker_training_run(
            args=args,
            config=config,
            metrics=metrics)
    else:
        # Local processing or on SageMaker container
        args = sagemaker_env_args(args=args, config=config)
        main(args)


class TrainingCommand(Command):
    def __init__(self, main, script=None, help=None, metrics=None, **training_args):
        super(TrainingCommand, self).__init__(help=help or 'Run training')
        if not script:
            script = main
        self.main = main
        self.script = script
        self.training_args = training_args
        self.config = None
        self.metrics = metrics

    def configure(self, parser: ArgumentParser):
        self.config = sagemaker_training_args(
            parser=parser,
            script=self.script,
            **self.training_args
        )

    def run(self, args):
        sagemaker_training_handle(
            args=args,
            config=self.config,
            main=self.main,
            metrics=self.metrics
        )


def sagemaker_training_main(
        main, script=None, script_fn=None, description=None, metrics=None,
        **training_args):
    r"""
    Entry point for training.

    Example
    -------

    .. code-block:: python

        from aws_sagemaker_remote import sagemaker_processing_main

        def main(args):
            # your code here
            pass

        if __name__ == '__main__':
            sagemaker_processing_main(
                main=main,
                # ... additional configuration
            )

    Parameters
    ----------
    main : function
        Main function. Must accept a single argument ``args`` (``argparse.Namespace``)
    script : str, optional
        Path to script file to execute. 
        Set to ``__file__`` for most use-cases.
        Empty or None defaults to file containing ``main``.
        Object interpreted as file containing the object.
    description: str, optional
        Script description for argparse
    metrics : dict, optional
        Metrics to record. Dictionary of metric name (str) to RegEx that extracts metric (str).
        See `SageMaker Training Metrics Docs <https://docs.aws.amazon.com/sagemaker/latest/dg/training-metrics.html#define-train-metric-regex>`_
    \**training_args : dict, optional
        Keyword arguments to :meth:`aws_sagemaker_remote.training.args.sagemaker_training_args`
    """
    # todo: detect module, class, etc. files
    return TrainingCommand(
        main=main, script=script,
        metrics=metrics, **training_args
    ).run_command(description=description)
