import multiprocessing
import traceback


def wrap_worker(fn, *args):
    semaphore.release()
    try:
        fn(*args)
    except Exception as e:
        print("exception in worker: {}".format(e))
        traceback.print_exc()
        raise e


def init_child(semaphore_):
    global semaphore
    semaphore = semaphore_


def run_workers(workers, fn, data, *args, expand=False, queue_size=100):
    assert workers > 0
    if workers > 1:
        assert queue_size > 0
        sem = multiprocessing.Semaphore(queue_size)
        with multiprocessing.Pool(workers, initializer=init_child, initargs=(sem,)) as pool:
            for datum in data:
                sem.acquire()
                if expand:
                    pool.apply_async(wrap_worker, (fn, *datum, *args))
                else:
                    pool.apply_async(wrap_worker, (fn, datum, *args))
            pool.close()
            pool.join()
    else:
        for datum in data:
            if expand:
                fn(*datum, *args)
            else:
                fn(datum, *args)
