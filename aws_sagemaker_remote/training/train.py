from ..session import sagemaker_session
from .config import SageMakerTrainingConfig
import os
from aws_sagemaker_remote.util.json_read import json_urlparse, json_converter
import json
from sagemaker.pytorch import PyTorch
from .channels import standardize_channels, upload_local_channels
from sagemaker.utils import name_from_base
from .iam import ensure_training_role
from .experiment import ensure_experiment
from ..git import git_get_tags
from ..tags import make_tags
from ..s3 import get_file_type, FileType
from sagemaker.inputs import TrainingInput
import warnings
from ..args import get_mode, get_s3_data_type
import tempfile
from urllib.parse import urlparse
from ..util.pipes import chunk_iterable
from sagemaker.s3 import S3Uploader
from sagemaker.inputs import ShuffleConfig
from aws_sagemaker_remote.ecr.images import ecr_ensure_image


def sagemaker_training_run(
    args,
    config: SageMakerTrainingConfig,
    metrics=None
):
    if os.getenv('SM_TRAINING_ENV', None):
        warnings.warn(
            "Trying to start a SageMaker container from a SageMaker container. Possible loop detected.")

    if metrics is None:
        metrics = {}
    session = sagemaker_session(
        profile_name=args.sagemaker_profile
    )
    image_uri = ecr_ensure_image(
        path=args.sagemaker_training_image,
        tag=args.sagemaker_training_image,
        accounts=args.sagemaker_training_image.split(","),
        session=session.boto_session
    )
    script = args.sagemaker_script
    script = os.path.abspath(script)
    source = args.sagemaker_source
    if not source:
        source = os.path.dirname(script)
    if not script.startswith(source):
        raise ValueError("script=[{}] must be in source=[{}]")
    entry_point = script[len(source)+1:]
    entry_point = entry_point.replace("\\", "/")
    metric_definitions = [
        {'Name': k, 'Regex': v}
        for k, v in metrics.items()
    ]
    dependencies = [getattr(args, k) for k in config.dependencies.keys()]
    print("Dependencies: {}".format(dependencies))

    # checkpoint_local_path='/opt/ml/checkpoints/'
    bucket = session.default_bucket()
    if args.sagemaker_job_name and args.sagemaker_job_name.strip():
        job_name = args.sagemaker_job_name
    else:
        job_name = name_from_base(args.sagemaker_base_job_name)
    tags = git_get_tags(script)
    tags["Source"] = 'aws-sagemaker-remote'
    tags["JobName"] = job_name
    tags["BaseJobName"] = args.sagemaker_base_job_name
    tags = make_tags(tags)
    #checkpoint_s3_uri = 's3://{}/{}/checkpoints'.format(bucket, job_name)
    input_prefix = "s3://{}/{}/inputs".format(bucket, job_name)
    iam = session.boto_session.client('iam')
    training_role = ensure_training_role(
        iam=iam, role_name=args.sagemaker_training_role)
    hyperparameters = {k.replace('_', '-'): str(v)
                       for k, v in vars(args).items() if v is not None and len(str(v)) > 0}
    hyperparameters['sagemaker-run'] = 'False'
    if args.sagemaker_checkpoint_s3 and args.sagemaker_checkpoint_s3 != 'default':
        if not args.sagemaker_checkpoint_s3.startswith('s3://'):
            raise ValueError(
                "--sagemaker-checkpoint-s3 must be an S3 URI (s3://...) or \"default\"")
        checkpoint_s3 = args.sagemaker_checkpoint_s3
    else:
        checkpoint_s3 = "s3://{}/{}/checkpoints".format(bucket, job_name)
    hyperparameters['checkpoint-dir'] = args.sagemaker_checkpoint_container
    if 'sagemaker-job-name' in hyperparameters:
        del hyperparameters['sagemaker-job-name']

    channels = config.inputs
    channels = {k: getattr(args, k) for k in channels.keys()}
    channels = {k: json_urlparse(v) for k, v in channels.items()}
    # and config.inputs[k].required == False}
    channels = {k: v for k, v in channels.items() if v}
    # for k,v in channels.items():
    #    if not v:
    #        raise ValueError("Channel [{}] is empty and required".format(k))
    channels = standardize_channels(channels=channels)
    channels = upload_local_channels(
        channels=channels, session=session, prefix=input_prefix)

    s3 = session.boto_session.client('s3')
    for k, v in channels.items():
        key = '{}-suffix'.format(k.replace('_', '-'))
        fileType = get_file_type(v, s3=s3)
        if fileType == FileType.FILE:
            hyperparameters[key] = os.path.basename(v)
        elif fileType == FileType.FOLDER:
            if key in hyperparameters:
                del hyperparameters[key]
        else:
            raise ValueError()

    chs = {}
    for k, v in channels.items():
        mode = getattr(args, "{}_mode".format(k))
        shuffle = getattr(args, "{}_shuffle".format(k))
        repeat = getattr(args, "{}_repeat".format(k))
        if (
            mode in [
                'AugmentedManifestFolder',
                'ManifestFolder'
            ]
        ):
            uri = urlparse(v)
            assert uri.scheme == 's3'
            bucket = uri.netloc
            key = uri.path.lstrip("/").rstrip("/")+"/"
            manifests = s3.list_objects_v2(
                Bucket=bucket,
                # Delimiter='string',
                # EncodingType='url',
                # MaxKeys=123,
                Prefix=key,
                # ContinuationToken='string',
                # FetchOwner=True|False,
                # StartAfter='string',
                # RequestPayer='requester',
                # ExpectedBucketOwner='string'
            )
            if 'Contents' not in manifests:
                raise ValueError("Cannot find contents of bucket [{}] key [{}]".format(
                    bucket, key))
            for i, manifest in enumerate(manifests['Contents']):
                mkey = manifest['Key'].lstrip('/')
                bn, _ = os.path.splitext(os.path.basename(mkey))
                s3_data = "s3://{}/{}".format(bucket, mkey)
                chs["{}_{}".format(k, bn.replace("-", "_"))] = TrainingInput(
                    s3_data=s3_data,
                    record_wrapping="RecordIO",
                    content_type='application/x-recordio',
                    s3_data_type=get_s3_data_type(mode),
                    input_mode=get_mode(mode),
                    attribute_names=config.inputs[k].attributes,
                    shuffle_config=ShuffleConfig(123+i) if shuffle else None
                )
                print("Adding manifest [{}] to input [{}]".format(s3_data, k))
        elif mode in [
            'File', 'Pipe', 'ManifestFile', 'AugmentedManifestFile'
        ]:
            if repeat > 1:
                for i in range(repeat):
                    chs["{}_repeat_{}".format(k, i)] = TrainingInput(
                        s3_data=v,
                        # distribution=None,
                        # compression=None,
                        # content_type=None,
                        record_wrapping="RecordIO" if get_mode(
                            mode) not in ['File'] else None,
                        content_type='application/x-recordio' if get_mode(
                            mode) not in ['File'] else None,
                        s3_data_type=get_s3_data_type(mode),
                        input_mode=get_mode(mode),
                        attribute_names=config.inputs[k].attributes,
                        shuffle_config=ShuffleConfig(
                            123+1) if shuffle else None
                        # target_attribute_name=None,
                        # shuffle_config=None,
                    )
            else:
                chs[k] = TrainingInput(
                    s3_data=v,
                    # distribution=None,
                    # compression=None,
                    # content_type=None,
                    record_wrapping="RecordIO" if get_mode(
                        mode) not in ['File'] else None,
                    content_type='application/x-recordio' if get_mode(
                            mode) not in ['File'] else None,
                    s3_data_type=get_s3_data_type(mode),
                    input_mode=get_mode(mode),
                    attribute_names=config.inputs[k].attributes,
                    shuffle_config=ShuffleConfig(123) if shuffle else None
                    # target_attribute_name=None,
                    # shuffle_config=None,
                )
        else:
            raise ValueError("Unknown mode: {}->{}".format(k, mode))
    channels = chs
    print("Hyperparameters: {}".format(hyperparameters))

    if not channels:
        channels = None
    print("Channels: {}".format(list(channels.keys())))
    #import pprint
    #pprint.pprint({k: v.config for k, v in channels.items()})
    #env = config.env

    estimator = PyTorch(
        sagemaker_session=session,
        base_job_name=args.sagemaker_base_job_name,
        entry_point=entry_point,
        source_dir=source,
        role=training_role,
        instance_type=args.sagemaker_training_instance,
        image_uri=image_uri,
        instance_count=1,
        framework_version='1.5.0',
        # hyperparameters=hyperparameters_from_argparse(vars(args)),
        metric_definitions=metric_definitions,
        dependencies=dependencies,
        checkpoint_s3_uri=checkpoint_s3,
        checkpoint_local_path=args.sagemaker_checkpoint_container,
        use_spot_instances=args.sagemaker_spot_instances,
        hyperparameters=hyperparameters,
        volume_size=args.sagemaker_volume_size,
        tags=tags,
        max_wait=args.sagemaker_max_wait if args.sagemaker_spot_instances else None,
        max_run=args.sagemaker_max_run
    )

    if args.sagemaker_experiment_name:
        sagemaker_client = session.boto_session.client('sagemaker')
        ensure_experiment(client=sagemaker_client,
                          experiment_name=args.sagemaker_experiment_name)
        experiment_config = {
            "ExperimentName": args.sagemaker_experiment_name
        }
        if args.sagemaker_trial_name:
            experiment_config["TrialName"] = args.sagemaker_trial_name
    else:
        if args.sagemaker_trial_name:
            raise ValueError(
                "If `sagemaker_trial_name` is provided, `sagemaker_experiment_name` must be provided as well")
        experiment_config = None

    estimator.fit(channels, job_name=job_name,
                  wait=False, experiment_config=experiment_config)
    job = estimator.latest_training_job
    if args.sagemaker_output_json:
        obj = job.describe()
        #print("Describe: {}".format(obj))
        os.makedirs(os.path.dirname(
            os.path.abspath(args.sagemaker_output_json)), exist_ok=True)
        with open(args.sagemaker_output_json, 'w') as f:
            json.dump(obj, f, default=json_converter, indent=4)

    if args.sagemaker_wait:
        job.wait(logs=True)  # args.sagemaker_logs)
    # todo:
    # use_spot_instances
    # experiment_config (dict[str, str]): Experiment management configuration.
    #            Dictionary contains three optional keys,
    #            'ExperimentName', 'TrialName', and 'TrialComponentDisplayName'.
    return estimator
