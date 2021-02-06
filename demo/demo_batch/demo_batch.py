from aws_sagemaker_remote.batch.main import BatchCommand, BatchConfig
import os
import argparse


def argparse_callback(parser: argparse.ArgumentParser):
    """
    Add any custom arguments you require
    """
    parser.add_argument(
        '--my-custom-flag', default="Default value", type=str, help='My custom flag'
    )


def env_callback(args):
    """
    Map custom arguments to Lambda environment variables
    """
    return {
        "MY_CUSTOM_FLAG": args.my_custom_flag
    }


def command():
    """
    Define defaults for your command
    """
    return BatchCommand(
        config=BatchConfig(
            stack_name='my-unique-stack-name',
            code_dir=os.path.abspath(os.path.join(
                __file__, '../lambda'
            )),
            description='Demo batch processing',
            argparse_callback=argparse_callback,
            env_callback=env_callback,
            webpack=True
        )
    )


def main():
    command().run_command(
        description="Demo batch processing"
    )


if __name__ == '__main__':
    main()
