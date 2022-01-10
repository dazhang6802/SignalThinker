import math
import multiprocessing
import threading
import time


class th(threading.Thread):
    def __init__(self, id):
        self.id = id
        threading.Thread.__init__(self)

    def run(self):
        while True:
            c = 0
            print("th:", self.id)
            time.sleep(1)


def func(msg, id):
    # t1 = th(id)
    # t1.start()
    while True:
        msg["testcode"] += 1
        for i in range(100000):
            c= math.sin(i % 3)
        print("task", id, time.time())
        #time.sleep(1)


if __name__ == "__main__":
    mdata = multiprocessing.Manager().dict()
    qdata = multiprocessing.Manager().Queue()

    mdata["testcode"] = 0

    pool = multiprocessing.Pool(20)

    for i in range(20):
        pool.apply_async(func, (mdata, i), )

    while True:
        # print(mdata["testcode"])
        time.sleep(1)
