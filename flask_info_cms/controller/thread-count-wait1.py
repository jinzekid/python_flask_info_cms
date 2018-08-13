# Author: Jason Lu
"""
使用mutexes在父/子主线程中探知线程何时结束
而不再使用time.sleep
"""
import _thread as thread
stdoutmeutex = thread.allocate_lock()
exitmutexes = [thread.allocate_lock() for i in range(10)]


def counter(myId, count):
    for i in range(count):
        stdoutmeutex.acquire()
        print('[%s] => %s' % (myId, i))
        stdoutmeutex.release()
    exitmutexes[myId].acquire() # 向主线程发送信号

for i in range(10):
    thread.start_new_thread(counter, (i, 100))

for mutex in exitmutexes:
    print('[%s]' % mutex.locked)
    while not mutex.locked():
        pass

print("main thread exiting...")