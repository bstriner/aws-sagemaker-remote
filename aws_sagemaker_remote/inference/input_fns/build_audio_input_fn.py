
from urllib.parse import urlparse
from aws_sagemaker_remote.inference.mime import JSON_TYPES
from aws_sagemaker_remote.inference.input_fns.json_input_wrap import json_input_wrap
from aws_sagemaker_remote.inference.input_fns.transcode_ffmpeg import transcode_ffmpeg


def build_audio_input_fn(sample_rate=None, channels=1):
    """
    Return a function that:

    - accepts requests
    - performs transcoding
    - returns tuple (sample_rate, samples)

    Include input_fn=build_audio_input_fn(...) in inference.py
    
    """
    def input_fn(request_body, request_content_type):
        data, extension, mime = json_input_wrap(
            request_body=request_body,
            request_content_type=request_content_type
        )
        print(f"json_input_wrap result: {type(data), len(data)}, extension: {extension}, mime: {mime}")
        if mime.startswith('audio/'):
            #ext = mimetypes.guess_extension(mime)
            data = transcode_ffmpeg(
                data=data,
                input_fmt=extension,
                sample_rate=sample_rate,
                channels=channels
            )
            return data
        else:
            raise ValueError(
                "Unsupported content type: \"{}\" (mime: {})".format(request_content_type, mime))
    return input_fn


if __name__ == '__main__':
    input_fns = [
        build_audio_input_fn(
            sample_rate=16000,
            channels=1
        ),
        build_audio_input_fn(
            sample_rate=8000,
            channels=1
        )
    ]
    input_files = [
        ['tests/test.wav', 'audio/x-wav'],
        ['tests/input.json', 'application/json'],
        ['tests/test.mp3', 'audio/mpeg']
    ]
    for i, input_fn in enumerate(input_fns):
        for input_file, mime in input_files:
            with open(input_file, 'rb') as f:
                body = f.read()
            fs, data = input_fn(body, mime)
            print(
                f"input_fn: {i}, file: {input_file}: fs: {fs}, data: {data.shape}")
