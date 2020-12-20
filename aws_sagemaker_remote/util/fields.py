from aws_sagemaker_remote.util.json_process import json_process


def get_field(data, field):
    data = json_process(data)
    original_data = data
    #print(data)
    if field:
        path = field.split('.')
        for p in path:
            if p not in data:
                raise ValueError("Field [{}] does not exist in data [{}]".format(field, original_data))
            data = data[p]
    return data
