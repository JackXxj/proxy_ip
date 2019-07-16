# coding:utf-8
__author__ = 'xxj'

import requests
import time
import re
import json
import redis
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

PROXY_LIST = []    # 代理ip列表


def get_proxy_ips(num):
    '''
    获取代理ip(快代理)
    :return:
    '''
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
        }
        url = 'https://dps.kdlapi.com/api/getdps/?orderid=903993353460865&num={num}&pt=1&format=json&sep=1'.format(num=num)
        response = requests.get(url=url, headers=headers, timeout=10)
        response_json = response.json()
        proxy_list = response_json.get('data').get('proxy_list')  # 代理ip列表
        for ip in proxy_list:
            PROXY_LIST.append(ip)
    except BaseException as e:
        print 'BaseException：', '代理ip异常', e
        # time.sleep(60)
        # return get_proxy_ips(num)


def file_write_redis(PROXY_LIST):
    '''
    将代理ip存储到各个爬虫项目下对应的redis中
    :return:
    '''
    r = redis.StrictRedis(host="172.31.10.75", port=9221)

    all_proxy(r, PROXY_LIST)


def all_proxy(r, PROXY_LIST):
    '''
    将代理ip写入到快代理redis中
    :param r:
    :return:
    '''
    kuai_proxy_length = r.scard('spider:kuai:proxy')  # 快代理
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的kuai代理ip数量：', kuai_proxy_length
    if kuai_proxy_length != 0:
        r.delete('spider:kuai:proxy')  # 清空reids中kuai代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中kuai列表'
    for proxy_ip in PROXY_LIST:
        r.sadd('spider:kuai:proxy', proxy_ip)

    kuai_proxy_length = r.scard('spider:kuai:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中kuai代理列表长度：', kuai_proxy_length


def main():
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'start'
    get_proxy_ips(200)
    print 'PROXY_LIST列表中代理ip的数量：', len(PROXY_LIST)
    if PROXY_LIST:
        file_write_redis(PROXY_LIST)
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'over'


if __name__ == '__main__':
    try:
        main()
    except BaseException as e:
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'main函数：', e
