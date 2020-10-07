
import json
def output_fn_json(prediction, content_type):

    if content_type == "application/json":
        return json.dumps(prediction), content_type
    else:
        raise ValueError("Unsupported content type: {}".format(content_type))