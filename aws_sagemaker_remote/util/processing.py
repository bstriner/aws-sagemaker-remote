import sagemaker

import pprint
from aws_sagemaker_remote.util.fields import get_field

#logger = logging.getLogger()
#logger.addHandler(logging.StreamHandler()) # Writes to console
#logger.setLevel(logging.DEBUG)
#logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
#logging.getLogger('urllib3').setLevel(logging.CRITICAL)

def processing_describe(job_name, client, field=None):
    description = processing_describe_get(job_name=job_name, client=client)
    description = get_field(description, field)
    return description


def processing_describe_get(client, job_name):
    description = client.describe_processing_job(
        ProcessingJobName=job_name
    )
    description['ProcessingInputs']={
        pi['InputName']: pi
        for pi in 
         description.get('ProcessingInputs', {})
    }
    description['ProcessingOutputConfig'] = description.get('ProcessingOutputConfig', {})
    description['ProcessingOutputConfig']['Outputs'] = {
        po['OutputName']: po
        for po in 
        description['ProcessingOutputConfig'].get('Outputs', {})
    }
    return description


if __name__ == '__main__':
    session = sagemaker.Session()
    client = session.boto_session.client('sagemaker')
    description = processing_describe(
        client=client, job_name='voxceleb-convert-vox2test-2020-10-07-09-23-16-900')
    print(description)