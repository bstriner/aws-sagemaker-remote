from aws_sagemaker_remote.mpworkers import run_workers
import time


def worker(i):
    print(i)
    return i


def test_multiprocessing():
    run_workers(
        8, worker, range(1000)
    )


if __name__ == '__main__':
    test_multiprocessing()
