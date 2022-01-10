import queue
import random
from multiprocessing import freeze_support
from multiprocessing.managers import BaseManager

# 建立2个队列，一个发送，一个接收
task_queue = queue.Queue()
result_queue = queue.Queue()


def get_task():
    return task_queue


def get_result():
    return result_queue


class QueueManager(BaseManager): pass


# 服务器的管理器上注册2个共享队列
QueueManager.register('get_task', callable=get_task)
QueueManager.register('get_result', callable=get_result)
# 设置端口，地址默认为空。验证码authkey需要设定。
manager = QueueManager(address=('', 8000), authkey=b'abc')


def manager_run():
    manager.start()
    # 通过管理器访问共享队列。
    task = manager.get_task()
    result = manager.get_result()

    # 对队列进行操作, 往task队列放进任务。
    for value in range(10):
        n = random.randint(0, 100)
        print('Put task %d' % n)
        task.put(n)
    # 从result队列取出结果
    print('Try get result...')
    try:
        for value in range(10):
            r = result.get(timeout=10)
            print('Result: %s' % r)
    except queue.Empty:
        print('result is empty')
    # 关闭管理器。
    manager.shutdown()
    print('master exit.')


if __name__ == '__main__':
    freeze_support()
    manager_run()
