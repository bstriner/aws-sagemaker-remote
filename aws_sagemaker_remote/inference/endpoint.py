import sagemaker
import click
import os
from botocore.exceptions import ClientError
from aws_sagemaker_remote.util.fields import get_field
from aws_sagemaker_remote.inference.local import inference_local
from aws_sagemaker_remote.inference.mime import MIME
import shutil
import glob


def endpoint_describe(name, client, field=None):
    description = client.describe_endpoint(EndpointName=name)
    description = get_field(description, field)
    return description


def endpoint_exists(name, client):
    try:
        endpoint_describe(name, client)
        return True
    except ClientError:
        return False


def endpoint_delete(name, client):
    client.delete_endpoint(EndpointName=name)


def endpoint_create(config, name, client, force):
    if not config:
        raise click.UsageError('Must specify endpoint config')
    if not name:
        name = config
    print("Creating endpoint [{}] from endpoint config [{}]".format(
        name, config
    ))
    if endpoint_exists(name=name, client=client):
        if force:
            print("Deleting existing endpoint")
            endpoint_delete(name=name, client=client)
            # todo: need to wait for delete to complete
        else:
            raise click.UsageError(
                'Specify force to overwrite existing endpoint')
    response = client.create_endpoint(
        EndpointName=name,
        EndpointConfigName=config)
    arn = response['EndpointArn']
    print("Created endpoint [{}]".format(arn))


def endpoint_invoke(model_dir, name, model, variant, input, output, input_type, input_glob, output_type, runtime_client):
    if not input:
        # todo: pipe and cli arguments
        raise click.UsageError("input is required")
    if not input_type:
        input_type, _ = MIME.guess_type(input)
        if not input_type:
            raise click.UsageError(
                'Cannot guess input type, specify input_type')
    if not output_type:
        output_type = 'application/json'
    if not os.path.exists(input):
        raise ValueError(f"Path `{input}` does not exist")
    if os.path.isfile(input):
        if input_glob:
            raise click.UsageError(
                "--input-glob only valid if --input is a directory")
        tasks = [
            (input, output)
        ]
    else:
        output = output or input
        input_glob = input_glob or "**/*"
        input_glob_path = os.path.join(input, input_glob)
        files = glob.glob(input_glob_path, recursive=True)
        tasks = [
            (file, "{}{}.out".format(output, file[len(input):]))
            for file in files
        ]
        if not len(tasks):
            print("Warning: no matches: `{input_glob_path}`")

    if model_dir:
        if name or model or variant:
            raise click.UsageError(
                "If a local model_dir is specified, do not specify name, model or variant")
        return inference_local(model_dir=model_dir, tasks=tasks,
                               input_type=input_type, output_type=output_type)
    else:
        kwargs = {}
        if model:
            kwargs['TargetModel'] = model
        if model:
            kwargs['TargetVariant'] = variant
        ret = None
        for input, output in tasks:
            with open(input, 'rb') as f:
                print("Invoking [{}] with data from [{}] ([{}]->[{}])".format(
                    name, input, input_type, output_type
                ))
                response = runtime_client.invoke_endpoint(
                    EndpointName=name,
                    Body=f,
                    ContentType=input_type,
                    Accept=output_type,
                    # CustomAttributes='string',
                    **kwargs
                    # TargetModel=model,
                    # TargetVariant=variant
                )
            output_data = response['Body']
            if output:
                os.makedirs(os.path.dirname(
                    os.path.abspath(output)), exist_ok=True)
                """
                if isinstance(result[0], str):
                    mode = 'w'
                elif isinstance(result[0], bytes):
                    mode='wb'
                else:
                    raise ValueError("Unknown result type: {}".format(type(result[0])))
                with open(output, mode) as f:
                    for chunk in result:
                        f.write(chunk)
                """

                with open(output, 'wb') as f:
                    shutil.copyfileobj(output_data, f)
                print("Saved to {}".format(output))
            else:
                ret = output_data
        return ret


if __name__ == '__main__':
    pass
