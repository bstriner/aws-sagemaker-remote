from aws_sagemaker_remote.s3 import parse_s3
import uuid
from aws_sagemaker_remote.util.logging_util import print_err


def create_job(
    session,
    manifest, report, arn, account_id,
    description, role_name, confirmation_required=True,
    ignore=0
):
    s3 = session.client('s3')
    s3control = session.client('s3control')
    manifest = parse_s3(manifest)
    report = parse_s3(report)

    response = s3.head_object(
        **manifest
    )
    manifest_arn = f"arn:aws:s3:::{manifest['Bucket']}/{manifest['Key']}"
    etag = response['ETag']
    etag = etag.strip("\"")
    manifest_location = {
        'ObjectArn': manifest_arn,
        'ETag': etag
    }
    if 'VersionId' in response:
        manifest_version_id = response['VersionId']
        manifest_location['ObjectVersionId'] = manifest_version_id,
    #print("manifest_location: {}".format(manifest_location))
    if report:
        report = {
            'Enabled': True,
            'Bucket': f"arn:aws:s3:::{report['Bucket']}",
            'Format': 'Report_CSV_20180820',
            'Prefix': report['Key'],
            'ReportScope': 'AllTasks'
        }
    else:
        print_err("Report disabled. Use `--report` to generate report.")
        report = {
            'Enabled': False
        }
    response = s3control.create_job(
        AccountId=account_id,
        ConfirmationRequired=confirmation_required,  # |False,
        Operation={
            'LambdaInvoke': {
                'FunctionArn': arn
            }
        },
        Report=report,
        # todo: test token
        ClientRequestToken=uuid.uuid4().hex,
        Manifest={
            'Spec': {
                # |'S3InventoryReport_CSV_20161130',
                'Format': 'S3BatchOperations_CSV_20180820',
                'Fields': [
                    'Bucket', 'Key'
                    # 'Ignore'|'Bucket'|'Key'|'VersionId',
                ] + (['Ignore'] * ignore)
            },
            'Location': manifest_location
        },
        Description=description,
        Priority=10,
        RoleArn=role_name
        # ,
        # Tags=[
        #     {
        #         'Key': 'Source',
        #         'Value': 'run_s3_batch'
        #     }
        # ]
    )
    if 'JobId' in response and response['JobId']:
        job_id = response['JobId']
        print(f"Created job [{job_id}]")
        if confirmation_required:
            print("Please confirm the job in the AWS Console.")
        return response
    else:
        raise ValueError(
            "Job did not create successfully: {}".format(str(response)))
