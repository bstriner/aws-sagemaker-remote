"""
Dummy inference script echoes input as output
"""

#print("Loaded inference.py: {}".format(__file__))


def model_fn(model_dir):
    """
    Load your model from model_dir
    """
    print("Running model_fn: {}".format(model_dir))
    return None


def input_fn(request_body, request_content_type):
    """
    Convert input for your model
    """
    print("Running input_fn")
    return request_body


def predict_fn(input_data, model):
    """
    Run your model
    """
    print("Running predict_fn")
    return input_data


def output_fn(prediction, content_type):
    """
    Convert model output
    """
    print("Running output_fn")
    return prediction, content_type
