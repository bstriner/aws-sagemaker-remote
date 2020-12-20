
from argparse import ArgumentParser, Namespace
import sys


class Command(object):
    def __init__(self, help=None):
        self.help = help

    def configure(self, parser: ArgumentParser):
        pass

    def run(self, args):
        pass

    def run_command(self, description=None):
        return run_command(self, description=description)


def run_command(command: Command, description=None):
    parser = ArgumentParser(description=description or command.help)
    command.configure(parser)
    args = parser.parse_args()
    return command.run(args)


def commands_parser(
    commands,
    description=None,
    parser=None,
    dest='command'
):
    if parser is None:
        description = description or "Experiment CLI"
        parser = ArgumentParser(description=description)
    parser_commands = parser.add_subparsers(
        title='command',
        dest=dest,
        help='Command to execute',
        # required=True todo: py 3.7 only
    )
    for k, command in commands.items():
        parser_command = parser_commands.add_parser(
            name=k, help=command.help
        )
        command.configure(parser_command)
    return parser


def handle_commands(commands, args):
    command = commands[args.command]
    vargs = vars(args)
    del vargs['command']
    args = Namespace(**vargs)
    return command.run(args)


def run_commands(commands, description=None, argv=None, dry_run=False):
    parser = commands_parser(
        commands=commands,
        description=description
    )
    if dry_run:
        return parser
    else:
        args = parser.parse_args(args=argv)
        if(not args.command):
            print("Command is required", file=sys.stderr)
            parser.print_usage(sys.stderr)
            sys.exit(1)
        return handle_commands(
            commands=commands,
            args=args
        )
