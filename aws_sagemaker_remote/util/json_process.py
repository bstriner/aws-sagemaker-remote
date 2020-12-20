def json_process(data):
    data = processing_json(data)
    data = batch_json(data)
    data = manifest_json(data)
    return data


def map_list(ar, key):
    if isinstance(ar, list):
        return {
            r[key]: r for r in ar
        }
    else:
        return ar


def manifest_json(description):
    if description:
        if 'Results' in description:
            description['Results'] = map_list(
                description['Results'],
                'TaskExecutionStatus')
            for k,v in description['Results'].items():
                bucket = v.get('Bucket', None)
                key = v.get('Key', None)
                if key and bucket:
                    description['Results'][k]['s3'] = f"s3://{bucket}/{key}"
    return description


def processing_json(description):
    if(description):
        if 'ProcessingInputs' in description:
            description['ProcessingInputs'] = map_list(
                description['ProcessingInputs'], 'InputName')
        if 'ProcessingOutputConfig' in description:
            if 'Outputs' in description['ProcessingOutputConfig']:
                description['ProcessingOutputConfig']['Outputs'] = map_list(
                    description['ProcessingOutputConfig']['Outputs'], 'OutputName'
                )
    return description


def batch_json(description):
    if description:
        job_id = description.get('JobId', None)
        report = description.get('Report', {})
        prefix = report.get('Prefix')
        bucket = report.get('Bucket')
        enabled = report.get('Enabled')
        if job_id and prefix and bucket and enabled:
            bucket = bucket.split(":")[-1]
            prefix = prefix.strip("/")
            description['Report']['s3'] = f"s3://{bucket}/{prefix}/job-{job_id}/manifest.json"
    return description


if __name__ == '__main__':
    data = {
        "Results": [
            {
                "TaskExecutionStatus": "succeeded"
            }
        ]
    }
    data = manifest_json(data)
    print(data)
