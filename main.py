from apscheduler.schedulers.blocking import BlockingScheduler
from sanic import Sanic
from sanic import response

# 初始化数据结构，读配置文件或数据库，写入model.controller 和 model.node
# 启动进程：信号机通信进程，代入变量 model.controller 共享变量
# 启动进程：路口优化，代入变量model.node
# 启动进程：定时器，代入变量model
# 启动web进程，开启rest服务

# ：multiprocessing.managers

app = Sanic(__name__)


@app.route("/get", methods=['GET'])
async def get_handler(request):
    return response.json({"Hello": "world"})


@app.route("/command", methods=['POST'])
async def post_handler(request):
    return response.text("ok")

# 增加一个静态调试页面，采用ajax以滚动条方式输出
# 增加一个telnet server，提供telnet服务，输出调试状态信息

app.run(host="0.0.0.0", port=80, debug=True)

scheduler = BlockingScheduler()
scheduler.add_job(fnc, 'interval', seconds=1)
scheduler.start()

if __name__ == '__main__':
    pass
    # See PyCharm help at https://www.jetbrains.com/help/pycharm/
