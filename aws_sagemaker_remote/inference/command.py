import mimetypes
from aws_sagemaker_remote.commands import Command
import importlib
from argparse import ArgumentParser
from aws_sagemaker_remote.util.fs import write_chunks


class InferenceCommandConfig(object):
    def __init__(
        self,
        module,
        input=None,
        output=None,
        model_dir=None,
        input_type=None,
        output_type='application/json'
    ) -> None:
        super().__init__()
        self.module = module
        self.model_dir = model_dir
        self.input = input
        self.input_type = input_type
        self.output = output
        self.output_type = output_type


def run_inference_module(
    config: InferenceCommandConfig
):
    input_type = config.input_type
    if not input_type:
        input_type, _ = mimetypes.guess_type(config.input)

    output_type = config.output_type
    if not output_type:
        output_type = 'application/json'

    module = importlib.import_module(config.module)
    model = module.model_fn(config.model_dir)
    with open(config.input, 'rb') as f:
        h = f.read()
    h = module.input_fn(h, input_type)
    h = module.predict_fn(h, model)
    h, _ = module.output_fn(h, output_type)
    write_chunks(
        path=config.output,
        chunks=h
    )


class InferenceCommand(Command):
    def configure(self, parser: ArgumentParser):
        parser.add_argument(
            '--module', default=self.config.module, type=str
        )
        parser.add_argument(
            '--model-dir', default=self.config.model_dir, type=str
        )
        parser.add_argument(
            '--input', default=self.config.input, type=str
        )
        parser.add_argument(
            '--input-type', default=self.config.input_type, type=str
        )
        parser.add_argument(
            '--output', default=self.config.output, type=str
        )
        parser.add_argument(
            '--output-type', default=self.config.output_type, type=str
        )
        pass

    def run(self, args):
        config = InferenceCommandConfig(
            module=args.module,
            input=args.input,
            input_type=args.input_type,
            output=args.output,
            output_type=args.output_type,
            model_dir=args.model_dir
        )
        run_inference_module(config)

    def __init__(self, config: InferenceCommandConfig, help='Run inference'):
        self.config = config
        super().__init__(help=help)
