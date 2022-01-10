import queue
import time
from multiprocessing.managers import BaseManager


class QueueManager(BaseManager): pass


# 从网络上的服务器上获取Queue，所以注册时只提供服务器上管理器注册的队列的名字:
QueueManager.register('get_task')
QueueManager.register('get_result')

server_addr = '127.0.0.1'
print('Connect to server %s...' % server_addr)
# b'abc'相当于'abc'.encode('ascii'),类型是bytes
m = QueueManager(address=(server_addr, 8000), authkey=b'abc')
# 连接服务器
m.connect()
# 获得服务器上的队列对象
task = m.get_task()
result = m.get_result()

for value in range(10):
    try:
        n = task.get(timeout=1)
        print('run task %d * %d...' % (n, n))
        r = '%d * %d = %d' % (n, n, n * n)
        time.sleep(1)
        result.put(r)
    except queue.Empty:
        print('task queue is empty')

print('worker exit.')
