import click
import os
import sys
from aws_sagemaker_remote.util.fs import write_chunks


def inference_handler(model_dir):
    if not os.path.exists(model_dir):
        raise ValueError(
            "Model directory [{}] does not exist".format(model_dir))
    try:
        from sagemaker_inference.default_handler_service import DefaultHandlerService
    except ImportError:
        raise click.UsageError(
            "Install sagemaker-inference to use local inference")

    sys.path.insert(0, os.path.join(model_dir, 'code'))
    handler = DefaultHandlerService()
    try:
        from mms.context import Context
    except ImportError:
        raise click.UsageError(
            "Install multi-model-server to use local inference")
    context = Context(
        model_name='local-model',
        model_dir=model_dir,
        manifest=None,
        batch_size=None,
        gpu=None,
        mms_version=None
    )
    handler.initialize(context)
    return handler, context


def inference_run(handler, context, input, output, input_type, output_type):

    try:
        from mms.context import RequestProcessor
    except ImportError:
        raise click.UsageError(
            "Install multi-model-server to use local inference")

    with open(input, 'rb') as f:
        data = f.read()
    context.request_processor = [RequestProcessor(
        request_header={
            'Content-Type': input_type,
            'Accept': output_type
        }
    )]
    data = [
        {'body': data}
    ]
    result = handler.handle(data, context)
    #print("Result: {}".format(result))
    status = context.get_response_status(0)
    # print(status)
    if status[0] != 200 and status[0].value != 200:
        raise ValueError("Invokation error: {}\n{}".format(
            status, "\n".join(result)))
    assert len(result) > 0
    if output:
        write_chunks(path=output, chunks=result)
        print("Saved to {}".format(output))
        return None
    else:
        return result


def inference_local(model_dir, input, output, input_type, output_type):
    handler, context = inference_handler(model_dir=model_dir)
    return inference_run(
        handler=handler, context=context, input=input,
        output=output, output_type=output_type, input_type=input_type)


if __name__ == '__main__':
    model_dir = "/mnt/c/Projects/speaker-identification/output/model"
    input1 = "/mnt/c/Projects/speaker-identification/data/test/16k (3).wav"
    input2 = "/mnt/c/Projects/speaker-identification/data/test/16k (4).wav"
    handler, context = inference_handler(model_dir=model_dir)

    res1 = inference_run(
        handler=handler, context=context, input=input1,
        output=None, output_type='application/json', input_type='audio/x-wav')
    print("res1: {}".format(res1))
    res2 = inference_run(
        handler=handler, context=context, input=input1,
        output=None, output_type='application/json', input_type='audio/x-wav')
    print("res2: {}".format(res2))
