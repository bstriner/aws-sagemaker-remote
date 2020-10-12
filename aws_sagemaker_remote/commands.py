
from argparse import ArgumentParser, Namespace


class Command(object):
    def __init__(self, help=None):
        self.help = help

    def configure(self, parser: ArgumentParser):
        pass

    def run(self, args):
        pass


def run_command(command: Command, description=None):
    parser = ArgumentParser(description=description or command.help)
    command.configure(parser)
    args = parser.parse_args()
    command.run(args)


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
        required=True)
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
    command.run(args)


def run_commands(commands, description=None, argv=None):
    parser = commands_parser(
        commands=commands,
        description=description
    )
    args = parser.parse_args(args=argv)
    handle_commands(
        commands=commands,
        args=args
    )
