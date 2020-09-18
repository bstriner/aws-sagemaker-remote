from .process import sagemaker_processing_run
from .args import sagemaker_processing_args
from argparse import ArgumentParser


def sagemaker_processing_main(
        script, main,
        **processing_args):
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
                script=__file__,
                main=main,
                # ...
            )
            
    Parameters
    ----------
    script : str
        Path to script file to execute. Set to ``__file__`` for most use-cases.
    main : function
        Main function. Must accept a single argument ``args:argparse.Namespace``.
    \**processing_args : dict
        Keyword arguments to :meth:`aws_sagemaker_remote.processing.args.sagemaker_processing_args`
    """
    parser = ArgumentParser()
    config = sagemaker_processing_args(parser=parser, script=script, **processing_args)
    args = parser.parse_args()
    if args.sagemaker_run:
        # Remote processing
        sagemaker_processing_run(
            args=args,
            config=config
        )
    else:
        # Local processing
        main(args)
