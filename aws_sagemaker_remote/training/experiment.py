
from smexperiments import experiment


def ensure_experiment(client, experiment_name):
    try:
        return experiment.Experiment.load(
            experiment_name=experiment_name, sagemaker_boto_client=client)
    except:
        print("Creating experiment `{}`".format(experiment_name))
        return experiment.Experiment.create(
            experiment_name=experiment_name, sagemaker_boto_client=client)
