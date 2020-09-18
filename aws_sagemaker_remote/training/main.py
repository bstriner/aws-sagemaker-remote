from .train import sagemaker_training_run
from .args import sagemaker_training_args
from argparse import ArgumentParser

def sagemaker_training_main(
        script, main, metrics=None,
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
                script=__file__,
                main=main,
                # ...
            )

    Parameters
    ----------
    script : str
        Path to script file to execute.  Set to ``__file__`` for most use-cases.
    main : function
        Main function. Must accept a single argument ``args`` (``argparse.Namespace``)
    metrics : dict
        Metrics to record. Dictionary of metric name (str) to RegEx that extracts metric (str).
    \**training_args : dict
        Keyword arguments to :meth:`aws_sagemaker_remote.training.args.sagemaker_training_args`
    """
    parser = ArgumentParser()
    config = sagemaker_training_args(parser=parser,script=script, **training_args)
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
