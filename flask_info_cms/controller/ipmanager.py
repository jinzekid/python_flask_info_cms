# Author: Jason Lu
import time
import urllib.request
import re
from threading import Thread, Lock
import controller.util as cutil
from controller.util import HeaderFactory
from controller.util import time_calcuate as tc

# 全局变量，需要下载的网页
#g_stack_download = []
g_stack_need_to_parse = []

class ManagerProxyIP(object):
    # 单利模式的锁
    _instance_lock = Lock()
    download_precent = 0
    total_page = 0
    show_precent = False
    debug = False
    download_tasks = []

    def __init__(cls, *args, **kwargs):
        if not hasattr(ManagerProxyIP, '_instance'):
            with ManagerProxyIP._instance_lock:
                if not hasattr(ManagerProxyIP, '_instance'):
                    ManagerProxyIP._instance = object.__new__(cls)

        return ManagerProxyIP._instance

    @classmethod
    def config(cls, debug=False):
        cls.debug = debug

    @classmethod
    def init_grab_ip_html(cls, start_page, end_page):
        """
        初始化页面下载链接地址，保存到下载栈中
        :param start_page: 起始页面
        :param end_page: 结束页面
        :return: 单例实例
        """
        url = "http://www.xicidaili.com/wn/"
        int_s_p = int(start_page)
        int_e_p = int(end_page)
        cnt = int_e_p - int_s_p + 1

        #global g_stack_download
        #g_stack_download = []

        if cls.debug:
            print(">>:一共下载网页数:%d" % cnt)

        for i in range(cnt):
            cur_page = int_e_p - i
            url_ip_html = url + str(cur_page)
            cls.download_tasks.append(url_ip_html)

        cls.total_page = len(cls.download_tasks)
        cls.show_precent = True

        print(cls.download_tasks)

    @classmethod
    def clear_tasks(cls):
        #global g_stack_download

        cls.download_tasks = cutil.clear_list(cls.download_tasks)

        #while len(cls.download_tasks) > 0:
        #    for obj in cls.download_tasks:
        #        cls.download_tasks.remove(obj)

        print("clear all tasks...%s" % cls.download_tasks)


##############################################################################
    """
    下载网页线程的多种方法
    """
    @classmethod
    def start_grab_ip_html(cls):
        """
        开启多线程，下载网页
        :return:
        """
        #global g_stack_download
        for url in cls.download_tasks:
            thread_download_html = ThreadDownloadIPHtml(url)
            thread_download_html.start()

    @classmethod
    def start_parse_ip_use_thread(cls):
        download_threads = ThreadDownloadIPHtml_use_thread(
            cls.download_tasks)
        download_threads.start(cls.download_finish)

    @classmethod
    def download_finish(cls, t, list_tasks_failed):
        #cls.download_precent = t#100
        if len(list_tasks_failed) > 0:
            print(">>:失败任务列表 %s" % list_tasks_failed)
        else:
            print(">>:所有网页下载完毕...%d" % t)
            cls.clear_tasks()

##############################################################################


    @classmethod
    def start_parse_ip(cls):
        global g_stack_need_to_parse
        for path_html in g_stack_need_to_parse:
            thread_parse_ip_html = ThreadParseIPHtml(path_html)
            thread_parse_ip_html.start()

    @classmethod
    def cal_download_precent(cls):
        flt_download_precent = 1 - (len(cls.stack_download) * 1.0) / \
                                 cls.total_page
        cls.download_precent = flt_download_precent * 100
        if cls.debug:
            print("下载进度: %f" % cls.download_precent)

        #if cls.download_precent >= 100:
        #    cls.show_precent = False

        return cls.download_precent

    @classmethod
    def save_ip_to_csv(cls, df_ip):
        """
        保存有用的IP地址，文件格式为csv
        :param df_ip:
        :return:
        """
        if df_ip.empty is not True:
            import pandas as pd
            df_ip.to_csv('res/ip.csv', index=False)
            print(">>:保存成功...")

    @classmethod
    def save_ip_to_mongodb(cls, df_ip):
        """
        保存有用的IP地址，到mongo数据库
        :param df_ip:
        :return:
        """

        pass

    ###########################解析方法#################################
    @classmethod
    def get_alive_minutes(cls, alive):
        total_minutes = 0
        if alive.find('天') != -1:
            str_time = alive.replace('天', '')
            total_minutes = int(str_time) * 24 * 60
        elif alive.find('小时') != -1:
            str_time = alive.replace('小时', '')
            total_minutes = int(str_time) * 60
        else:
            str_time = alive.replace('分钟', '')
            total_minutes = int(str_time)

        return total_minutes

    @classmethod
    def bs4_paraser(cls, html):
        from bs4 import BeautifulSoup
        import re
        all_values = []
        value = {}
        soup = BeautifulSoup(html, 'html.parser')

        # 获取影评的部分
        all_div = soup.find_all('tr')
        for row in all_div:
            dict_ip_info = {}
            all_td = row.find_all('td')

            if len(all_td) > 1:
                str_ip = re.findall(r"<td>(.+?)</td>", str(all_td[1]))[0]
                dict_ip_info['ip'] = str_ip

                str_port = re.findall(r"<td>(.+?)</td>", str(all_td[2]))[0]
                dict_ip_info['port'] = int(str_port)

                str_alive = \
                re.findall(r"<td>(.+?)</td>", str(all_td[len(all_td) - 2]))[0]
                dict_ip_info['alive'] = ManagerProxyIP.get_alive_minutes(
                    str_alive)

                all_values.append(dict_ip_info)

        return all_values

    # 测试IP地址是否有用
    @classmethod
    def get_useful_ip_address(cls, df_ip):
        list_ip_address = []
        test_url = 'https://httpbin.org/anything/test_ip'
        import urllib.request
        import time
        for index, dict_ip_info in df_ip.iterrows():
            print(dict_ip_info['ip'])
            ip_address = dict_ip_info['ip']
            ip_port = dict_ip_info['port']

            proxy = urllib.request.ProxyHandler(
                {'https': '%s:%s' % (ip_address, ip_port)})
            # 是否开启DebugLog
            httphd = urllib.request.HTTPHandler(debuglevel=0)
            opener = urllib.request.build_opener(proxy, httphd)

            # 创建全局默认的opener对象
            urllib.request.install_opener(opener)

            # 使用添加报头
            req = urllib.request.Request(test_url)
            header_infos = HeaderFactory().header_info
            for info in header_infos:
                list_info = list(info)
                req.add_header(list_info[0], list_info[1])

            try:
                data = urllib.request.urlopen(req, timeout=6).read().decode(
                    'utf-8')
                if data is not None:
                    list_ip_address.append(dict_ip_info)
                    print(data)
                    print('good ip address:' + ip_address)
                    print('================================')
            except Exception as e:
                print('请求超时...' + str(e))

            #time.sleep(2)

        return list_ip_address
############################################################

import threading
import time

"""
方法一：使用threading子类
网页下载线程
"""
class ThreadDownloadIPHtml(threading.Thread):

    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        """
        下载网页
        """
        headers = HeaderFactory().header_info
        opener = urllib.request.build_opener()
        opener.addheaders = headers

        print(">>:开始抓取url:%s" % (self.url))
        list_url = re.split('/', self.url)

        str_html = 'res/ip_%s.html' % (list_url[-1])
        try:
            data = opener.open(self.url).read()
            fhandle = open(str_html, 'wb')
            fhandle.write(data)
            fhandle.close()
            print('>>:finished save ip html....%s' % (str_html))

            # 出栈
            global g_stack_download
            global g_stack_need_to_parse
            g_stack_download.remove(self.url)
            g_stack_need_to_parse.append(str_html)
        except Exception as e:
            print(">>:download exception:%s" % e)
        else:
            print('>>:剩余需要下载的网页')
            print(g_stack_download)
            print('==================')
            print('>>:需要解析的网页: %s' % (str_html))
            print('==================')

"""
方法二：使用底层_thread
下载网页
"""
import _thread as thread
import os
class ThreadDownloadIPHtml_use_thread(object):

    thread_lock = thread.allocate_lock()

    def __init__(self, tasks):
        self.tasks = tasks
        self.thread_mutexs = [False] * len(tasks)
        self.error_task = []

        print("ThreadDownloadIPHtml_use_thread current pid: %d"
              "" % (os.getpid()))
        print("Task numbers: %d" % len(tasks))

        #print(">>:开启新进程...")
        #self.f = ForkDownloadIPHtml()
        #self.f.start()

    def task(self, i, url):
        """
        下载网页
        :return:
        """
        self.thread_lock.acquire()
        headers = HeaderFactory().header_info
        opener = urllib.request.build_opener()
        opener.addheaders = headers

        print(">>:开始抓取url:%s" % (url))
        list_url = re.split('/', url)

        str_html = 'res/ip_%s.html' % (list_url[-1])
        try:
            data = opener.open(url).read()
            fhandle = open(str_html, 'wb')
            fhandle.write(data)
            fhandle.close()
            #print('>>:finished save ip html....%s' % (str_html))
        except Exception as e:
            # 移除该网页
            self.thread_mutexs[i] = True
            self.error_task.append({'id': i, 'url': url})
            print(">>:download exception:%s" % e)
        else:
            #print('>>:需要解析的网页: %s' % (str_html))
            #print('==================')
            #print('id=%d, 线程: %s' % (i, thread.get_ident()))
            self.thread_mutexs[i] = True

        #time.sleep(2)
        self.thread_lock.release()
        pass

    @tc
    def start(self, func_complete= None):
        for i in range(len(self.tasks)):
            url = self.tasks[i]
            thread.start_new_thread(self.task, (i, url))

        while False in self.thread_mutexs:
            pass

        print(':>>下载结束...')
        if func_complete: func_complete(100, self.error_task)


"""
使用进程fork, 下载页面
"""
class ForkDownloadIPHtml(object):

    def __init__(self):
        pass

    def start(self):
        while True:
            new_pid = os.fork()
            if new_pid == 0: # 子进程
                self.child()
            else:
                print('Hello from parent %s, child p:%s' % (os.getpid(),
                                                            new_pid))

            if input() == 'q': break

    def child(self):
        print('hello from child', os.getpid())
        os._exit(0) # 否则将回到父循环中



# 解析ip网页内容
class ThreadParseIPHtml(threading.Thread):

    def __init__(self, ip_html):
        threading.Thread.__init__(self)
        self.ip_html = ip_html

    def run(self):
        """
        解析IP网页内容
        """
        print(">>:开始解析ip地址...")
        import pandas as pd
        with open(self.ip_html, 'r') as f:
            data = f.read()
            list_ip_address = ManagerProxyIP.bs4_paraser(data)

            data = pd.DataFrame(
                list_ip_address[:10],
                columns=['ip', 'port', 'alive']
            )
            list_avaliable_ip = ManagerProxyIP.get_useful_ip_address(
                data.sort_values(by='alive', ascending=False))

            df_avalibable_ip = pd.DataFrame((list_avaliable_ip))

            print(">>:解析结束...")
            print("=================%s=======================" % self.ip_html)
            print(df_avalibable_ip)
            print("===========================================")

