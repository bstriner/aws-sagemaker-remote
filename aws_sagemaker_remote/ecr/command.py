from aws_sagemaker_remote.commands import Command
from aws_sagemaker_remote.ecr.images import Image, ecr_ensure_image
from argparse import ArgumentParser
from aws_sagemaker_remote.args import bool_argument
import sagemaker
import boto3


class BuildImageCommand(Command):
    def __init__(self, image: Image, help='Build docker image'):
        self.image = image
        super().__init__(help=help)

    def configure(self, parser: ArgumentParser):
        # parser.add_argument(
        #    '--name', default=self.image.name, type=str
        # )
        parser.add_argument(
            '--profile', default='default', type=str
        )
        parser.add_argument(
            '--path', default=self.image.path, type=str
        )
        parser.add_argument(
            '--tag', default=self.image.tag, type=str
        )
        parser.add_argument(
            '--accounts', default=",".join(self.image.accounts), type=str
        )
        bool_argument(parser, '--force', default=True,
                      help="If image already exists in ECR, do nothing")
        bool_argument(parser, '--pull', default=True,
                      help="Pull latest version of FROM images if building")
        bool_argument(parser, '--push', default=True,
                      help="Push results to ECR")
        bool_argument(parser, '--cache', default=True,
                      help='Use cached layers during build')
        bool_argument(parser, '--wsl', default=False,
                      help='WSL path fix')
        for k, v in self.image.download_files.items():
            flag = "--{}".format(k.replace("_", "-"))
            parser.add_argument(
                flag, default=v, type=str, help=f"Download auxiliary file (default: {v})"
            )

        return super().configure(parser)

    def run(self, args):
        session = boto3.Session(profile_name=args.profile)
        image = Image(
            # name=args.name,
            path=args.path,
            tag=args.tag,
            accounts=args.accounts.split(","),
            download_files={
                k: getattr(args, k) for k in self.image.download_files.keys()
            }
        )
        ecr_ensure_image(
            image=image,
            force=args.force,
            session=session,
            pull=args.pull,
            cache=args.cache,
            push=args.push,
            wsl=args.wsl
        )
