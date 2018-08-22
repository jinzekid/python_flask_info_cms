# Author: Jason Lu
import time
import re
import os
import urllib.request
import _thread as thread
from threading import Thread, Lock
from enum import Enum

import controller.util as cutil
from controller.util import HeaderFactory
from controller.util import time_calcuate as tc

# 全局变量，需要下载的网页
#g_stack_download = []
#g_stack_need_to_parse = []

MS = Enum('MS', 'none loading_htmls finish_download can_parse_ips parsing_ips '
                'finish_parse_ips')

class ManagerProxyIP(object):
    # 单利模式的锁
    _instance_lock = Lock()
    download_precent = 0
    total_page = 0
    debug = False
    download_tasks = []
    parse_tasks = []

    # 私有变量
    _g_status = MS.none


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
    def status(cls):
        if cls._g_status == MS.loading_htmls:
            return "loading_htmls2"
        elif cls._g_status == MS.can_parse_ips:
            return "can_parse_ips2"
        elif cls._g_status == MS.none:
            return "none"
        elif cls._g_status == MS.finish_parse_ips:
            return "finish_parsing2"

        return cls._g_status

    @classmethod
    def set_status(cls, status):
        cls._g_status = status

    @classmethod
    def init_grab_ip_html(cls, start_page, end_page):
        """
        初始化页面下载链接地址，保存到下载栈中
        :param start_page: 起始页面
        :param end_page: 结束页面
        :return: 单例实例
        """
        url = "http://www.xicidaili.com/wn/"
        print(start_page, " ===" , end_page)
        int_s_p = int(start_page)
        int_e_p = int(end_page)
        cnt = int_e_p - int_s_p + 1


        if cls.debug:
            print(">>:一共下载网页数:%d" % cnt)

        for i in range(cnt):
            cur_page = int_e_p - i
            url_ip_html = url + str(cur_page)
            cls.download_tasks.append(url_ip_html)

        cls.total_page = len(cls.download_tasks)
        cls._g_status = MS.loading_htmls
        print(cls.download_tasks)

    @classmethod
    def clear_tasks(cls):
        cls.download_tasks = cutil.clear_list(cls.download_tasks)
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
        for url in cls.download_tasks:
            thread_download_html = ThreadDownloadIPHtml(url)
            thread_download_html.start()


    @classmethod
    def start_download_ip_use_thread(cls):
        cls._g_status = MS.loading_htmls

        print(">>:开始启动多线程下载网页...%s" % cls._g_status)
        download_threads = ThreadDownloadIPHtml_use_thread(cls.download_tasks)
        download_threads.start(cls.download_finish)

    @classmethod
    def download_finish(cls, t, tasks_failed, tasks_parse):

        # 保存需要解析的网址
        print(">>:需要解析的网址列表: %s" % cls.parse_tasks)
        print(">>:222需要解析的网址列表: %s" % tasks_parse)

        cls.parse_tasks = tasks_parse
        if len(tasks_failed) > 0:
            print(">>:失败任务列表 %s" % tasks_failed)
        else:
            print(">>:所有网页下载完毕...%d" % t)
            cls._g_status = MS.can_parse_ips
            print(">>:g_status: %s" % cls._g_status)
            cls.clear_tasks()

        # 开始解析ip地址
        #cls.start_parse_ip_use_thread()

    @classmethod
    def finish_parse(cls):
        cls._g_status = MS.finish_parse_ips

##############################################################################
    """
    解析已经下载的地址
    """
    @classmethod
    def start_parse_ip(cls):
        for path_html in cls.parse_tasks:
            thread_parse_ip_html = ThreadParseIPHtml(path_html)
            thread_parse_ip_html.start()

    @classmethod
    def start_parse_ip_use_sub_thread(cls):
        print(">>:开始启动多线程解析...")
        cls._g_status = MS.parsing_ips

        t = ParseIP_Use_SubThread(cls.parse_tasks)
        t.start_sub_thread_to_parse(func_complete=cls.finish_parse)
        pass

    @classmethod
    def start_parse_ip_use_basic_thread(cls):
        print(">>:开始启动解析多线程...")
        download_threads = ThreadParseIPHtml(cls.parse_tasks)
        download_threads.start_parse(func_complete=cls.save_ip_to_csv)
        pass

##############################################################################


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
        headers = HeaderFactory().header_info # 工厂方法获取请求头信息
        opener = urllib.request.build_opener()
        opener.addheaders = headers # 添加头部信息

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

class ThreadDownloadIPHtml_use_thread(object):

    thread_lock = thread.allocate_lock()

    def __init__(self, tasks):
        self.tasks = tasks
        self.thread_mutexs = [False] * len(tasks)
        self.error_task = []
        self.parse_htmls = []

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
            self.parse_htmls.append(str_html)

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
        if func_complete: func_complete(100, self.error_task, self.parse_htmls)



# 解析ip网页内容
"""
使用底层_thread方法解析
"""
import pandas as pd
class ThreadParseIPHtml(object):

    def __init__(self, parse_htmls):
        self.parse_htmls = parse_htmls
        self.thread_mutex = [False] * len(parse_htmls)
        self.all_avaliable_ips = None

    def start_parse(self, func_complete=None):

        if len(self.parse_htmls) <= 0:
            print(">>:似乎没有需要解析的网页，解析结束:(")
            return

        for i in range(len(self.parse_htmls)):
            str_html = self.parse_htmls[i]
            thread.start_new_thread(self.parsing_html, (i, str_html,))

        while False in self.thread_mutex:pass

        print(">>:解析完毕...")
        if func_complete:
            func_complete(self.all_avaliable_ips)

    def parsing_html(self, i, ip_html):
        """
        解析IP网页内容
        """
        print(">>:开始解析ip地址...")

        with open(ip_html, 'r') as f:
            data = f.read()
            list_ip_address = ManagerProxyIP.bs4_paraser(data)

            data = pd.DataFrame(
                list_ip_address,
                columns=['ip', 'port', 'alive']
            )
            list_avaliable_ip = ManagerProxyIP.get_useful_ip_address(
                data.sort_values(by='alive', ascending=False))

            df_avalibable_ip = pd.DataFrame((list_avaliable_ip))

            print(">>:解析结束...%s" % ip_html)
            #print("=================%s=======================" % self.ip_html)
            #print(data)

            if not df_avalibable_ip.empty:
                if self.all_avaliable_ips is None:
                    self.all_avaliable_ips = df_avalibable_ip
                else:
                    self.all_avaliable_ips = pd.merge(self.all_avaliable_ips, df_avalibable_ip)
            else:
                print(">>:没有可用地址: %s" % ip_html)

            print(">>:所有可用的ip地址:")
            print(self.all_avaliable_ips)
            print("===========================================")
            self.thread_mutex[i] = True

"""
使用Thread子类进行ip的解析
"""
class ParseIP_Use_SubThread(object):

    """
    方法一：使用
    """
    def __init__(self, parse_htmls):
        self.stdoutmutex = threading.Lock()
        self.parse_htmls = parse_htmls
        self.all_avaliable_ips = None
        self.threads = []

        print(">>:初始化 %s" % self.__class__)

    def start_sub_thread_to_parse(self, func_complete):

        for i in range(len(self.parse_htmls)):
            thread = ThreadParseIP_SubThread(self.parse_htmls[i],
                                             self.all_avaliable_ips,
                                             self.stdoutmutex)
            thread.start()
            self.threads.append(thread)


        print(">>:一共开始 %d 个线程解析地址" % len(self.parse_htmls))
        for t in self.threads:
            t.join() # 等待所有thread线程执行完成

        print(">>:解析完成: ---------")
        if func_complete: func_complete()
        pass


class ThreadParseIP_SubThread(threading.Thread):

    def __init__(self, parse_html, avaliable_ips, mutex):
        self.parse_html = parse_html
        self.avaliable_ips = avaliable_ips # 共享对象，不是全局对象
        self.mutex = mutex
        threading.Thread.__init__(self)

    def run(self):
        """
        同上一样解析地址
        :return:
        """
        with open(self.parse_html, 'r') as f:
            data = f.read()
            list_ip_address = ManagerProxyIP.bs4_paraser(data)
            data = pd.DataFrame(list_ip_address[:5],
                                columns=['ip', 'port', 'alive'])
            list_avaliable_ip = ManagerProxyIP.get_useful_ip_address(
                data.sort_values(by='alive', ascending=False))
            df_avaliable_ip = pd.DataFrame(list_avaliable_ip)
            print(">>:解析结束...%s" % self.parse_html)

            with self.mutex:
                print("=================%s=======================" % self.parse_html)
                print(data)

        pass



