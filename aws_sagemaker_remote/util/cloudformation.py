from aws_sagemaker_remote.util.logging_util import print_err
import time


def get_cloudformation_output(cloudformation, stack_name, output_key):
    stack = get_cloudformation(
        cloudformation=cloudformation, stack_name=stack_name)
    if isinstance(output_key, str):
        return get_stack_output(stack, output_key)
    elif isinstance(output_key, (list, tuple)):
        return tuple(get_stack_output(stack, k) for k in output_key)
    else:
        raise ValueError(
            "Parameter `output_key` should be string, list, or tuple, got {}".format(type(output_key)))


def delete_stack(cloudformation, stack_name):
    response = cloudformation.delete_stack(
        StackName=stack_name,
        # RetainResources=[
        #    'string',
        # ],
        # RoleARN='string',
        # ClientRequestToken='string'
    )


def get_stack_output(stack, output_key):
    if stack and 'Outputs' in stack:
        for output in stack['Outputs']:
            if output['OutputKey'] == output_key:
                return output['OutputValue']
    return None


def stack_exists(cloudformation, stack_name):
    return get_cloudformation(cloudformation, stack_name) is not None


def stack_ready(cloudformation, stack_name):
    stack = get_cloudformation(cloudformation, stack_name)
    if not stack:
        return False
    status = stack['StackStatus']
    if status in ['UPDATE_COMPLETE', 'CREATE_COMPLETE']:
        return True
    if status in ['ROLLBACK_COMPLETE']:
        print_err(
            f"Stack {stack_name} is in status [{status}]. Deleting stack."
        )
        delete_stack(cloudformation, stack_name)
        return stack_ready(cloudformation, stack_name)
    if status.endswith('PROGRESS'):
        while status.endswith('PROGRESS'):
            print_err(
                f"Stack {stack_name} is in status [{status}]. Waiting.",
            )
            time.sleep(10)
            stack = get_cloudformation(cloudformation, stack_name)
            if not stack:
                return False
            status = stack['StackStatus']
        return stack_ready(cloudformation, stack_name)
    else:
        print_err(f"Stack {stack_name} is in status [{status}].")
    return False


def get_cloudformation(cloudformation, stack_name):
    try:
        response = cloudformation.describe_stacks(
            StackName=stack_name
        )
        # print(response)
    except:
        response = None
    if response:
        response = response['Stacks']
        if len(response) > 0:
            return response[0]
    return None
