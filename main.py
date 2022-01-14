# -*- coding: utf-8 -*-
import multiprocessing
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from sanic import Sanic
from sanic import response


def traffic_data_function(cf,stat):
    while True:
        stat["volume"] += 1
        time.sleep(1)


def asc_function(cfg, stat):
    def task1s():
        stat["time"] = time.time()
        print(stat["time"])

    def task5s():
        print("5s")

    sche = BlockingScheduler()
    sche.add_job(task1s, "interval", seconds=1)
    sche.add_job(task5s, "interval", seconds=5)
    sche.start()


app = Sanic(__name__)


# 对外输出信息
@app.route("/get", methods=['GET'])
async def get_handler(request):
    global status
    return response.json({"Hello": "world", "time": status["time"],"volume":status["volume"]})


# 对内控制与提交信息
@app.route("/command", methods=['POST'])
async def post_handler(request):
    b = request.args
    print(b)
    return response.text("ok")


if __name__ == "__main__":
    config = multiprocessing.Manager().dict()
    config["mk"] = 0
    status = multiprocessing.Manager().dict()
    status["time"] = 0
    status["volume"] = 0

    asc_task = multiprocessing.Process(target=asc_function, args=(config, status))
    asc_task.start()
    traffic_data_task= multiprocessing.Process(target=traffic_data_function, args=(config, status))
    traffic_data_task.start()
    app.run(host="0.0.0.0", port=80, workers=4, debug=False, access_log=False)
