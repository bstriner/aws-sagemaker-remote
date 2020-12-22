
from io import BytesIO
from scipy.io import wavfile
from urllib.parse import urlparse
import subprocess
from aws_sagemaker_remote.inference.mime import FIX_FORMATS


def transcode_ffmpeg(data, input_fmt='wav', sample_rate=None, channels=1, codec='pcm_s16le'):
    """
    Transcode binary data in given format to wav file with resampling

    Use pipes and run in-memory
    """
    assert input_fmt, "input_fmt is required in transcode_ffmpeg"
    if input_fmt.lower() in FIX_FORMATS:
        input_fmt = FIX_FORMATS[input_fmt.lower()]
    #print(f"transcode_ffmpeg input_fmt: {input_fmt}")
    cmd = [
        'ffmpeg',
        '-f', input_fmt,  # input format
        '-i', 'pipe:'  # input pipe
    ]
    if sample_rate:
        cmd.extend(['-ar', str(sample_rate)])  # sample rate
    if channels:
        cmd.extend(['-ac', str(channels)])  # channels
    if codec:
        cmd.extend(['-acodec', codec])  # pcm_s16le, etc
    cmd.extend([
        '-f', 'wav',  # output format
        'pipe:1'  # output pipe
    ])
    proc = subprocess.run(
        cmd,
        # capture_output=True,
        input=data,
        check=True,
        stdout=subprocess.PIPE
    )
    fs, data = wavfile.read(BytesIO(proc.stdout))
    return fs, data
