from aws_sagemaker_remote.training.main import sagemaker_training_main
import aws_sagemaker_remote
import glob
import os
import json


def main(args):
    print(f"Args: {vars(args)}")
    print(f"checkpoint: {args.checkpoint_dir}")
    files = list(glob.glob(
        os.path.join(args.checkpoint_dir, "**", "*"),
        recursive=True
    ))
    print(f"checkpoint files: {files}")
    with open(os.path.join(args.checkpoint_dir, 'sm-checkpoint-1.json'), 'w') as f:
        json.dump({"step": 123, "files": files}, f)
    print("complete")


if __name__ == '__main__':
    sagemaker_training_main(
        main=main,  # main function for local execution
        dependencies={
            # Add a module to SageMaker
            # module name: module path
            'aws_sagemaker_remote': aws_sagemaker_remote
        },
        #configuration_command='pip3 install --upgrade sagemaker sagemaker-experiments',
        # Name the job
        base_job_name='demo-checkpoint',
        volume_size=20
    )

"""
aws --profile default s3 sync demo/demo-checkpoint s3://sagemaker-us-east-1-683880991063/demo-checkpoint
aws --profile default s3 ls s3://sagemaker-us-east-1-683880991063/demo-checkpoint/
python demo/demo_checkpoint.py --sagemaker-run yes --sagemaker-checkpoint-s3 s3://sagemaker-us-east-1-683880991063/demo-checkpoint
"""
