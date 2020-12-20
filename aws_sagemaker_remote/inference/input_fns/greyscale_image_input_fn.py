
import torch
from .image_input_fn import input_fn as image_input_fn


def input_fn(request_body, request_content_type):
    """
    Convert input for your model
    """
    print("Running greyscale_image_input_fn")
    tensor = image_input_fn(request_body, request_content_type)
    if tensor.size(0) > 1:
        tensor = torch.mean(tensor, dim=0, keepdim=True)
    return tensor
