import tempfile
from .process import sagemaker_processing_run
from .args import sagemaker_processing_args
from argparse import ArgumentParser, Namespace
import inspect
from ..commands import Command, run_command
from .config import SageMakerProcessingConfig
from sagemaker.s3 import S3Uploader
from ..session import sagemaker_session


class ProcessingCommand(Command):
    def __init__(
            self,
            script, main, help=None,
            **processing_args
    ):
        super(ProcessingCommand, self).__init__(
            help=help or 'SageMaker processing'
        )

        if not script:
            script = inspect.getfile(main)
        self.script = script
        self.main = main
        self.processing_args = processing_args
        self.config = None

    def configure(self, parser: ArgumentParser):
        self.config = sagemaker_processing_args(
            parser=parser,
            script=self.script,
            **self.processing_args)

    def run(self, args):
        sagemaker_processing_handle(
            args=args,
            config=self.config,
            main=self.main
        )


def sagemaker_processing_local_args(args, config: SageMakerProcessingConfig):
    argv = vars(args)
    tmps = {}
    uris = {}
    for k, v in config.outputs.items():
        if argv[k] and argv[k].startswith("s3://"):
            tmps[k] = tempfile.TemporaryDirectory()
            uris[k] = argv[k]
            argv[k] = tmps[k].__enter__()
    return Namespace(**argv), tmps, uris


def sagemaker_processing_handle(
    args, config, main
):
    if args.sagemaker_run:
        # Remote processing
        sagemaker_processing_run(
            args=args,
            config=config
        )
    else:
        # Local processing
        args, tmps, uris = sagemaker_processing_local_args(
            args=args, config=config)
        try:
            main(args)
            if tmps:
                session = sagemaker_session(profile_name=args.sagemaker_profile)
                for k in tmps.keys():
                    S3Uploader.upload(
                        local_path=getattr(args, k),
                        desired_s3_uri=uris[k],
                        sagemaker_session=session
                    )
        finally:
            for tmp in tmps.values():
                tmp.__exit__()


def sagemaker_processing_main(
    main, script=None, description=None,
    **processing_args
):
    r"""
    Entry point for processing.

    Example
    -------

    .. code-block:: python

        from aws_sagemaker_remote import sagemaker_training_main

        def main(args):
            # your code here
            pass

        if __name__ == '__main__':
            sagemaker_training_main(
                main=main,
                # ... additional configuration
            )

    Parameters
    ----------
    main : function
        Main function. Must accept a single argument ``args:argparse.Namespace``.
    script : str, optional
        Path to script file to execute. 
        Set to ``__file__`` for most use-cases.
        Empty or None defaults to file containing ``main``.
    description: str, optional
        Script description for argparse
    \**processing_args : dict, optional
        Keyword arguments to :meth:`aws_sagemaker_remote.processing.args.sagemaker_processing_args`
    """
    command = ProcessingCommand(
        script=script,
        main=main,
        **processing_args
    )
    run_command(command, description=description)
