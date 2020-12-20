
from PIL import Image
import numpy
from io import BytesIO
import torch


def input_fn(request_body, request_content_type):
    """
    Convert input for your model
    """
    print("Running image_input_fn")
    buffer = BytesIO(request_body)
    image = Image.open(buffer)
    array = numpy.array(image)
    tensor = torch.from_numpy(array).float()/255.
    tensor = tensor.permute(2, 0, 1)
    return tensor
