import boto3
import csv
import json
import sagemaker
import os
import codecs
from aws_sagemaker_remote.s3 import get_file_string, get_file
from aws_sagemaker_remote.util.batch import batch_describe
from aws_sagemaker_remote.util.cli_argument import cli_argument


def batch_report(session, job, output):
    if isinstance(session, boto3.Session):
        session = sagemaker.Session(boto_session=session)
    job = [
        cli_argument(j, session=session)
        for j in job
    ]
    report_manifests = [
        batch_describe(
            session=session,
            job_id=j,
            field='Report.s3'
        ) for j in job
    ]
    for rm in report_manifests:
        assert rm, "Missing report manifest"
    report_manifests.reverse()
    failure_set = set()
    success_set = set()
    s3 = session.boto_session.client('s3')
    os.makedirs(output, exist_ok=True)
    success_report = os.path.join(output, 'success.csv')
    failure_report = os.path.join(output, 'failure.csv')
    info_file = os.path.join(output, 'info.json')
    success_reports = []
    failure_reports = []
    for rm in report_manifests:
        rms = get_file_string(s3=s3, url=rm)
        rms = json.loads(rms)
        results = rms['Results']
        print("Report keys: {}".format(
            r['TaskExecutionStatus'] for r in results))
        succeeded = next(
            (res for res in results
                if res['TaskExecutionStatus'] == 'succeeded'),
            None)
        failed = next(
            (res for res in results
                if res['TaskExecutionStatus'] == 'failed'),
            None)
        if succeeded:
            bucket = succeeded['Bucket']
            key = succeeded['Key']
            url = f"s3://{bucket}/{key}"
            print(f"Succeeded: {url}")
            success_reports.append(url)

        if failed:
            bucket = failed['Bucket']
            key = failed['Key']
            url = f"s3://{bucket}/{key}"
            print(f"Failed: {url}")
            failure_reports.append(url)

    with open(success_report, 'w', newline='') as fsuccess:
        wsuccess = csv.writer(fsuccess)
        for sr in success_reports:
            with get_file(url=sr, s3=s3) as fi:
                reader = codecs.getreader('utf-8')(fi)
                for row in csv.reader(reader):
                    file_url = f"s3://{row[0]}/{row[1]}"
                    if file_url not in success_set:
                        wsuccess.writerow(row)
                        success_set.add(file_url)

    with open(failure_report, 'w', newline='') as ffailure:
        wfailure = csv.writer(ffailure)
        for fr in failure_reports:
            with get_file(url=fr, s3=s3) as fi:
                reader = codecs.getreader('utf-8')(fi)
                for row in csv.reader(reader):
                    file_url = f"s3://{row[0]}/{row[1]}"
                    if file_url not in success_set and file_url not in failure_set:
                        wfailure.writerow(row)
                        failure_set.add(file_url)

    info = {
        "success": len(success_set),
        "failure": len(failure_set),
    }
    with open(info_file, 'w') as f:
        json.dump(info, f)
    print("Success: {}, failure: {}".format(info['success'], info['failure']))


if __name__ == '__main__':
    session = boto3.Session(profile_name='default')
    session = sagemaker.Session(boto_session=session)
    batch_report(
        session,
        [
            'ee1e7233-2668-4320-9fff-e13613bd7622',
            '7ba2b3d0-c4a5-4c6a-98d7-10842ae02256',
            '5a758d9e-1348-4c15-9f0f-32590794eb4a'
        ],
        output="output/batch-report"
    )
