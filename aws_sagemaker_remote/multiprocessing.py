import multiprocessing
import traceback

def wrap_worker(fn, *args):
    try:
        fn(*args)
    except Exception as e:
        print("exception in worker: {}".format(e))
        traceback.print_exc()
        raise e


def run_workers(workers, fn, data, *args, expand=False):
    if workers > 1:
        with multiprocessing.Pool(workers) as pool:
            tasks = [
                (
                    pool.apply_async(wrap_worker, (fn, *datum, *args))
                    if expand else
                    pool.apply_async(wrap_worker, (fn, datum, *args))
                )
                for datum in data
            ]
            tasks = [task.get() for task in tasks]
    else:
        tasks = [
            fn(datum, *args)
            for datum in data
        ]
    return tasks
