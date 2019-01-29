# coding:utf-8
__author__ = 'xxj'

import requests
import time
import re
import json
from rediscluster import StrictRedisCluster
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

PROXY_LIST = []    # 代理ip列表

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
}


def get_proxy_ips(num):
    '''
    获取代理ip
    :return:
    '''
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
        }
        url = 'https://proxyapi.mimvp.com/api/fetchsecret.php?orderid=860068921904605585&num={num}&http_type=3&result_fields=1,2,3&result_format=json'.format(num=num)
        response = requests.get(url=url, headers=headers, timeout=10)
        ip_list = json.loads(response.text).get('result')
        if not ip_list:
            print time.strftime('[%Y-%m-%d %H:%M:%S]'), '获取代理ip异常：', response.text
            content_json = response.json()
            code_msg = content_json.get('code_msg')  # 异常信息
            code_msg = code_msg.encode('utf-8')
            search_obj = re.search(r'.*?，【(.*?)秒】', code_msg, re.S)
            stop_time = search_obj.group(1)
            stop_time = int(stop_time)
            print '代理ip接口限制,限制时间为：', stop_time, '秒'
            # time.sleep(stop_time)
            # return get_proxy_ips(num)
        for ip in ip_list:
            ip = ip.get('ip:port')
            PROXY_LIST.append(ip)
    except BaseException as e:
        print 'BaseException：', '代理ip异常'
        # time.sleep(60)
        # return get_proxy_ips(num)


def file_write_redis(PROXY_LIST):
    '''
    将代理ip存储到各个爬虫项目下对应的redis中
    :return:
    '''
    startup_nodes = [{'host': 'redis2', 'port': '6379'}]
    r = StrictRedisCluster(startup_nodes=startup_nodes, decode_responses=True)

    baike_crawler(r, PROXY_LIST)    # 百度百科
    baidu_news_hot(r, PROXY_LIST)    # 百度新闻热词(天任务)
    baidu_news_hot_hour(r, PROXY_LIST)    # 百度新闻热词（小时任务）
    baidu_news_webpage(r, PROXY_LIST)    # 百度新闻网页

    da_zhong_dian_ping(r, PROXY_LIST)    # 大众点评优惠券

    jizhan(r, PROXY_LIST)    # 基站
    wifi(r, PROXY_LIST)    # wifi

    wbsearch_and_bdnews(r, PROXY_LIST)    # 微博搜索和百度新闻联调
    weibo(r, PROXY_LIST)    # 微博
    weibo_user(r, PROXY_LIST)    # 微博用户
    weibo_user_info(r, PROXY_LIST)    # 微博用户信息
    weibo_user_follow(r, PROXY_LIST)    # 微博用户关注用户
    weibo_user_follower(r, PROXY_LIST)    # 微博用户粉丝用户
    weibo_user_content(r, PROXY_LIST)    # 微博用户内容

    pconline(r, PROXY_LIST)    # 太平洋网

    pubg_friends(r, PROXY_LIST)    # pubg的好友
    pubg_match(r, PROXY_LIST)    # pubg的比赛信息
    pubg_death(r, PROXY_LIST)    # pubg的团队死亡信息

    wrd(r, PROXY_LIST)    # 微热点

    game_17173_search(r, PROXY_LIST)  # 17173搜索
    sina_search_news(r, PROXY_LIST)  # 新浪搜索


def baike_crawler(r, PROXY_LIST):
    '''
    将代理ip写入baike_crawler中
    :return:
    '''
    baike_crawler_proxy_length = r.llen('spider:baike_crawler:proxy')    # baike_crawler代理长度
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的baike_crawler代理ip数量：', baike_crawler_proxy_length
    if baike_crawler_proxy_length != 0:
        r.delete('spider:baike_crawler:proxy')    # 清空reids中baike_crawler代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中baike_crawler的代理ip'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:baike_crawler:proxy', proxy_ip)

    baike_crawler_proxy_length = r.llen('spider:baike_crawler:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中baike_crawler代理列表长度：', baike_crawler_proxy_length


def baidu_news_hot(r, PROXY_LIST):
    '''
    将代理ip写入baidu_news_hot中
    :param r:
    :return:
    '''
    baidu_news_hot_proxy_length = r.llen('spider:baidu_news_hot:proxy')  # baidu_news_hot
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的baidu_news_hot代理ip数量：', baidu_news_hot_proxy_length
    if baidu_news_hot_proxy_length != 0:
        r.delete('spider:baidu_news_hot:proxy')  # 清空reids中baidu_news_hot代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中baidu_news_hot列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:baidu_news_hot:proxy', proxy_ip)

    baidu_news_hot_proxy_length = r.llen('spider:baidu_news_hot:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中baidu_news_hot代理列表长度：', baidu_news_hot_proxy_length


def baidu_news_hot_hour(r, PROXY_LIST):
    '''
    将代理ip写入baidu_news_hot_hour中
    :param r:
    :return:
    '''
    baidu_news_hot_hour_proxy_length = r.llen('spider:baidu_news_hot_hour:proxy')  # baidu_news_hot
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的baidu_news_hot_hour代理ip数量：', baidu_news_hot_hour_proxy_length
    if baidu_news_hot_hour_proxy_length != 0:
        r.delete('spider:baidu_news_hot_hour:proxy')  # 清空reids中baidu_news_hot_hour代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中baidu_news_hot_hour列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:baidu_news_hot_hour:proxy', proxy_ip)

    baidu_news_hot_hour_proxy_length = r.llen('spider:baidu_news_hot_hour:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中baidu_news_hot_hour代理列表长度：', baidu_news_hot_hour_proxy_length


def baidu_news_webpage(r, PROXY_LIST):
    '''
    将代理ip写入到baidu_news_webpage中
    :param r:
    :return:
    '''
    baidu_news_webpage_proxy_length = r.llen('spider:baidu_news_webpage:proxy')  # baidu_news_webpage
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的baidu_news_webpage代理ip数量：', baidu_news_webpage_proxy_length
    if baidu_news_webpage_proxy_length != 0:
        r.delete('spider:baidu_news_webpage:proxy')  # 清空reids中baidu_news_webpage代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中baidu_news_webpage列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:baidu_news_webpage:proxy', proxy_ip)

    baidu_news_webpage_proxy_length = r.llen('spider:baidu_news_webpage:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中baidu_news_webpage代理列表长度：', baidu_news_webpage_proxy_length


def da_zhong_dian_ping(r, PROXY_LIST):
    '''
    将代理ip写入到da_zhong_dian_ping中
    :param r:
    :return:
    '''
    da_zhong_dian_ping_proxy_length = r.llen('spider:da_zhong_dian_ping:proxy')  # da_zhong_dian_ping
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的da_zhong_dian_ping代理ip数量：', da_zhong_dian_ping_proxy_length
    if da_zhong_dian_ping_proxy_length != 0:
        r.delete('spider:da_zhong_dian_ping:proxy')  # 清空reids中da_zhong_dian_ping代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中da_zhong_dian_ping列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:da_zhong_dian_ping:proxy', proxy_ip)

    da_zhong_dian_ping_proxy_length = r.llen('spider:da_zhong_dian_ping:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中da_zhong_dian_ping代理列表长度：', da_zhong_dian_ping_proxy_length


def jizhan(r, PROXY_LIST):
    '''
    将代理ip写入到jizhan中
    :param r:
    :return:
    '''
    jizhan_proxy_length = r.llen('spider:jizhan:proxy')  # jizhan
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的jizhan代理ip数量：', jizhan_proxy_length
    if jizhan_proxy_length != 0:
        r.delete('spider:jizhan:proxy')  # 清空reids中jizhan代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中jizhan列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:jizhan:proxy', proxy_ip)

    jizhan_proxy_length = r.llen('spider:jizhan:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中jizhan代理列表长度：', jizhan_proxy_length


def wifi(r, PROXY_LIST):
    '''
    将代理ip写入到wifi中
    :param r:
    :return:
    '''
    wifi_proxy_length = r.llen('spider:wifi:proxy')  # wifi
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的wifi代理ip数量：', wifi_proxy_length
    if wifi_proxy_length != 0:
        r.delete('spider:wifi:proxy')  # 清空reids中wifi代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中wifi列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:wifi:proxy', proxy_ip)

    wifi_proxy_length = r.llen('spider:wifi:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中wifi代理列表长度：', wifi_proxy_length


def wbsearch_and_bdnews(r, PROXY_LIST):
    '''
    将代理ip写入到wbsearch_and_bdnews中
    :param r:
    :return:
    '''
    wbsearch_and_bdnews_proxy_length = r.llen('spider:wbsearch_and_bdnews:proxy')  # wbsearch_and_bdnews
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的wbsearch_and_bdnews代理ip数量：', wbsearch_and_bdnews_proxy_length
    if wbsearch_and_bdnews_proxy_length != 0:
        r.delete('spider:wbsearch_and_bdnews:proxy')  # 清空reids中wbsearch_and_bdnews代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中wbsearch_and_bdnews列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:wbsearch_and_bdnews:proxy', proxy_ip)

    wbsearch_and_bdnews_proxy_length = r.llen('spider:wbsearch_and_bdnews:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中wbsearch_and_bdnews代理列表长度：', wbsearch_and_bdnews_proxy_length


def weibo(r, PROXY_LIST):
    '''
    将代理ip写入到weibo中
    :param r:
    :return:
    '''
    weibo_proxy_length = r.llen('spider:weibo:proxy')  # weibo
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的weibo代理ip数量：', weibo_proxy_length
    if weibo_proxy_length != 0:
        r.delete('spider:weibo:proxy')  # 清空reids中weibo代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中weibo列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:weibo:proxy', proxy_ip)

    weibo_proxy_length = r.llen('spider:weibo:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中weibo代理列表长度：', weibo_proxy_length


def weibo_user(r, PROXY_LIST):
    '''
    将代理ip写入到weibo_user中(微博用户抓取项目)
    :param r:
    :return:
    '''
    weibo_user_proxy_length = r.llen('spider:weibo_user:proxy')  # weibo_user
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的weibo_user代理ip数量：', weibo_user_proxy_length
    if weibo_user_proxy_length != 0:
        r.delete('spider:weibo_user:proxy')  # 清空reids中weibo_user代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中weibo_user列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:weibo_user:proxy', proxy_ip)

    weibo_user_proxy_length = r.llen('spider:weibo_user:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中weibo_user代理列表长度：', weibo_user_proxy_length


def weibo_user_info(r, PROXY_LIST):
    '''
    将代理ip写入到weibo_user_info中(微博用户信息抓取项目)
    :param r:
    :return:
    '''
    weibo_user_info_proxy_length = r.llen('spider:weibo_user_info:proxy')  # weibo_user_info
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的weibo_user_info代理ip数量：', weibo_user_info_proxy_length
    if weibo_user_info_proxy_length != 0:
        r.delete('spider:weibo_user_info:proxy')  # 清空reids中weibo_user_info代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中weibo_user_info列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:weibo_user_info:proxy', proxy_ip)

    weibo_user_info_proxy_length = r.llen('spider:weibo_user_info:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中weibo_user_info代理列表长度：', weibo_user_info_proxy_length


def weibo_user_follow(r, PROXY_LIST):
    '''
    将代理ip写入到weibo_user_follow中(微博用户关注用户抓取项目)
    :param r:
    :return:
    '''
    weibo_user_follow_proxy_length = r.llen('spider:weibo_user_follow:proxy')  # weibo_user_follow
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的weibo_user_follow代理ip数量：', weibo_user_follow_proxy_length
    if weibo_user_follow_proxy_length != 0:
        r.delete('spider:weibo_user_follow:proxy')  # 清空reids中weibo_user_follow代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中weibo_user_follow列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:weibo_user_follow:proxy', proxy_ip)

    weibo_user_follow_proxy_length = r.llen('spider:weibo_user_follow:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中weibo_user_follow代理列表长度：', weibo_user_follow_proxy_length


def weibo_user_follower(r, PROXY_LIST):
    '''
    将代理ip写入到weibo_user_follower中(微博粉丝用户抓取项目)
    :param r:
    :return:
    '''
    weibo_user_follower_proxy_length = r.llen('spider:weibo_user_follower:proxy')  # weibo_user_follower
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的weibo_user_follower代理ip数量：', weibo_user_follower_proxy_length
    if weibo_user_follower_proxy_length != 0:
        r.delete('spider:weibo_user_follower:proxy')  # 清空reids中weibo_user_follower代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中weibo_user_follower列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:weibo_user_follower:proxy', proxy_ip)

    weibo_user_follower_proxy_length = r.llen('spider:weibo_user_follower:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中weibo_user_follower代理列表长度：', weibo_user_follower_proxy_length


def weibo_user_content(r, PROXY_LIST):
    '''
    将代理ip写入到weibo_user_content中(微博用户发布的微博抓取项目)
    :param r:
    :return:
    '''
    weibo_user_content_proxy_length = r.llen('spider:weibo_user_content:proxy')  # weibo_user_content
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的weibo_user_content代理ip数量：', weibo_user_content_proxy_length
    if weibo_user_content_proxy_length != 0:
        r.delete('spider:weibo_user_content:proxy')  # 清空reids中weibo_user_content代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中weibo_user_content列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:weibo_user_content:proxy', proxy_ip)

    weibo_user_content_proxy_length = r.llen('spider:weibo_user_content:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中weibo_user_content代理列表长度：', weibo_user_content_proxy_length


def pconline(r, PROXY_LIST):
    '''
    将代理ip写入到pconline中
    :param r:
    :return:
    '''
    pconline_proxy_length = r.llen('spider:pconline:proxy')  # pconline
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的pconline代理ip数量：', pconline_proxy_length
    if pconline_proxy_length != 0:
        r.delete('spider:pconline:proxy')  # 清空reids中weibo代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中pconline列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:pconline:proxy', proxy_ip)

    pconline_proxy_length = r.llen('spider:pconline:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中pconline代理列表长度：', pconline_proxy_length


def pubg_friends(r, PROXY_LIST):
    '''
    将代理ip写入pubg_friends中
    :return:
    '''
    pubg_friends_proxy_length = r.llen('spider:pubg_friends:proxy')    # pubg_friends代理长度
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的pubg_friends代理ip数量：', pubg_friends_proxy_length
    if pubg_friends_proxy_length != 0:
        r.delete('spider:pubg_friends:proxy')    # 清空reids中pubg_friends代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中pubg_friends的代理ip'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:pubg_friends:proxy', proxy_ip)

    pubg_friends_proxy_length = r.llen('spider:pubg_friends:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中pubg_friends代理列表长度：', pubg_friends_proxy_length


def pubg_match(r, PROXY_LIST):
    '''
    将代理ip写入pubg_match中
    :return:
    '''
    pubg_match_proxy_length = r.llen('spider:pubg_match:proxy')    # pubg_match代理长度
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的pubg_match代理ip数量：', pubg_match_proxy_length
    if pubg_match_proxy_length != 0:
        r.delete('spider:pubg_match:proxy')    # 清空reids中pubg_match代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中pubg_match的代理ip'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:pubg_match:proxy', proxy_ip)

    pubg_match_proxy_length = r.llen('spider:pubg_match:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中pubg_match代理列表长度：', pubg_match_proxy_length


def pubg_death(r, PROXY_LIST):
    '''
    将代理ip写入pubg_death中
    :return:
    '''
    pubg_death_proxy_length = r.llen('spider:pubg_death:proxy')    # pubg_death代理长度
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的pubg_death代理ip数量：', pubg_death_proxy_length
    if pubg_death_proxy_length != 0:
        r.delete('spider:pubg_death:proxy')    # 清空reids中pubg_death代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中pubg_death的代理ip'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:pubg_death:proxy', proxy_ip)

    pubg_death_proxy_length = r.llen('spider:pubg_death:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中pubg_death代理列表长度：', pubg_death_proxy_length


def wrd(r, PROXY_LIST):
    '''
    将代理ip写入wrd中
    :return:
    '''
    wrd_proxy_length = r.llen('spider:wrd:proxy')  # wrd
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的wrd代理ip数量：', wrd_proxy_length
    if wrd_proxy_length != 0:
        r.delete('spider:wrd:proxy')  # 清空reids中wrd代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中wrd列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:wrd:proxy', proxy_ip)

    wrd_proxy_length = r.llen('spider:wrd:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中wrd代理列表长度：', wrd_proxy_length


def game_17173_search(r, PROXY_LIST):
    '''
    将代理ip写入game_17173_search中
    :return:
    '''
    game_17173_search_proxy_length = r.llen('spider:game_17173_search:proxy')  # game_17173_search
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的game_17173_search代理ip数量：', game_17173_search_proxy_length
    if game_17173_search_proxy_length != 0:
        r.delete('spider:game_17173_search:proxy')  # 清空reids中game_17173_search代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中game_17173_search列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:game_17173_search:proxy', proxy_ip)

    game_17173_search_proxy_length = r.llen('spider:game_17173_search:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中game_17173_search代理列表长度：', game_17173_search_proxy_length


def sina_search_news(r, PROXY_LIST):
    '''
    将代理ip写入sina_search_news中
    :return:
    '''
    sina_search_news_proxy_length = r.llen('spider:sina_search_news:proxy')  # sina_search_news
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中遗留的sina_search_news代理ip数量：', sina_search_news_proxy_length
    if sina_search_news_proxy_length != 0:
        r.delete('spider:sina_search_news:proxy')  # 清空reids中sina_search_news代理列表
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), '清空redis中sina_search_news列表'
    for proxy_ip in PROXY_LIST:
        r.lpush('spider:sina_search_news:proxy', proxy_ip)

        sina_search_news_proxy_length = r.llen('spider:sina_search_news:proxy')
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'redis中sina_search_news代理列表长度：', sina_search_news_proxy_length


def main():
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'start'
    get_proxy_ips(100)
    print 'PROXY_LIST列表中代理ip的数量：', len(PROXY_LIST)
    if PROXY_LIST:
        file_write_redis(PROXY_LIST)
    print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'over'


if __name__ == '__main__':
    try:
        main()
    except BaseException as e:
        print time.strftime('[%Y-%m-%d %H:%M:%S]'), 'main函数：', e
