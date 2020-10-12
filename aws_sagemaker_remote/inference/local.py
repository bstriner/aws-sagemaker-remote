import click
import os
import sys


def inference_local(model_dir, input, output, input_type, output_type):
    try:
        from sagemaker_inference.default_handler_service import DefaultHandlerService
    except ImportError:
        raise click.UsageError(
            "Install sagemaker-inference to use local inference")

    try:
        from mms.context import Context, RequestProcessor
    except ImportError:
        raise click.UsageError(
            "Install multi-model-server to use local inference")

    sys.path.insert(0, os.path.join(model_dir, 'code'))

    with open(input, 'rb') as f:
        data = f.read()
    handler = DefaultHandlerService()
    context = Context(
        model_name='local-model',
        model_dir=model_dir,
        manifest=None,
        batch_size=None,
        gpu=None,
        mms_version=None
    )
    context.request_processor = [RequestProcessor(
        request_header={
            'Content-Type': input_type,
            'Accept': output_type
        }
    )]
    data = [
        {'body': data}
    ]
    handler.initialize(context)
    result = handler.handle(data, context)
    #print("Result: {}".format(result))
    status = context.get_response_status(0)
    #print(status)
    if status[0] != 200 and status[0].value != 200:
        raise ValueError("Invokation error: {}\n{}".format(status, "\n".join(result)))
    assert len(result) > 0
    if output:
        os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
        if isinstance(result[0], str):
            mode = 'w'
        elif isinstance(result[0], bytes):
            mode='wb'
        else:
            raise ValueError("Unknown result type: {}".format(type(result[0])))
        with open(output, mode) as f:
            for chunk in result:
                f.write(chunk)
        print("Saved to {}".format(output))
        return None
    else:
        return result
    # return "data"
