import threading
import time


# import logging


class thd(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = False

    def run(self):
        while True:
            time.sleep(1)
            print(time.time())
            if self.stop:
                break

    def close(self):
        self.stop = True


if __name__ == "__main__":
    fn=open("sysconfig.json","r")
    txt=fn.readlines()
    fn.close()
    a=json.loads(txt)
    t = thd()
    t.start()
    print(t.is_alive())
    time.sleep(5)
    t.close()
    print(t.is_alive())
