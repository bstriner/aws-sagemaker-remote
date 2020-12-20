import json
import torch
import numpy as np


class TensorEncoder(json.JSONEncoder):
    """
    Encode numpy objects as lists, otherwise return the default JSON encoding
    """
    def default(self, obj):
        if torch.is_tensor(obj):
            obj = obj.detach().cpu().numpy()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def output_fn(prediction, content_type):
    """
    Convert model output. Numpy objects are converted to nested lists.
    """
    print("Running json_output_fn")
    if content_type == 'application/json':
        return json.dumps(prediction, cls=TensorEncoder), content_type
    else:
        raise ValueError("Unknown content type: {}".format(content_type))
