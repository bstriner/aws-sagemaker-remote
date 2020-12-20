import json
import os
from aws_sagemaker_remote.s3 import get_file


def s3_concat(session, manifest, output, limit):
    s3 = session.boto_session.client('s3')
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, 'wb') as fo:
        with open(manifest) as f:
            for i, line in enumerate(f):
                info = json.loads(line)
                ref = info['file-ref']
                with get_file(
                    url=ref,
                    s3=s3
                ) as data:
                    fo.write(data.read())
                if limit and i + 1 >= limit:
                    break
    print(f"Concatenated {i+1} files")
