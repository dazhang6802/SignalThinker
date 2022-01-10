import time

from apscheduler.schedulers.blocking import BlockingScheduler


def start():
    sche.start()


def stop():
    sche.stop()


def close():
    sche.stop()


def run():
    pass


def va():
    print("va",time.time())


def time_table():
    print("timeplan",time.time())


sche = BlockingScheduler()
sche.add_job(va, 'interval', seconds=0.1)
sche.add_job(time_table, 'interval', seconds=1)
sche.start()