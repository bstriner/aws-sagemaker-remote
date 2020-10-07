from scipy.io import wavfile
import io

def input_fn_wav(request_body, request_content_type):
    if request_content_type in ['audio/wav', 'audio/wave']:
        fs, data = wavfile.read(io.BytesIO(request_body))
        return fs, data
    else:
        raise ValueError(
            "Unsupported content type: {}".format(request_content_type))
