import time

from apscheduler.schedulers.blocking import BlockingScheduler


def start():
    scheduler.start()


def stop():
    scheduler.stop()


def close():
    scheduler.stop()

def run():
    print(round(time.time(),2))


scheduler = BlockingScheduler()
scheduler.add_job(run, 'interval', seconds=0.25)

if __name__=="__main__":
    start()


