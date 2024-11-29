"""
爬取B站《黑神话悟空》最终预告视频的最新评论信息（包括发布者昵称、性别、所在地和评论内容）
"""

import requests
import json
import urllib3
urllib3.disable_warnings()
import pymongo
import hashlib
import time
from urllib.parse import quote

class BiliBiliSpider:
    # 评论数据所在的api的url
    url = "https://api.bilibili.com/x/v2/reply/wbi/main"

    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Origin": "https://www.bilibili.com",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    }

    # cookie信息
    cookies = {
        "Cookie": "CURRENT_FNVAL=4048; buvid3=D66F2E5D-F0D9-AB64-A8FD-941723FC2A3392506infoc; b_nut=1705374792; i-wanna-go-back=-1; b_ut=7; _uuid=17889FD10-D78D-C57D-10FA6-988CA347C35794471infoc; enable_web_push=DISABLE; home_feed_column=5; browser_resolution=1536-742; buvid4=7042D1B8-3F1D-283A-73DF-F6BC128CAC7593593-024011603-xRRPtdQGG22UbEFUl%2FWLTA%3D%3D; buvid_fp=016f77f3882d3fe23ac9f079802f41d7; rpdid=|(umYuJ)|kRJ0J'u~|lJ~R~m~; bsource=search_google; header_theme_version=CLOSE; SESSDATA=690915aa%2C1748390645%2Cede37%2Ab1CjC4cnzznsjMAdKttljjT59EeCIWN1xHtiAQMUEM4vt9I6tiF4CUQXOUJuveFR0FWrgSVm9PRWpRX3QtR2pRVUdFQ3duR29Xa0l1UWk4NTZsV1RXWm9wR0kyeW8zMWtBWDNNVVVTODVFT1JhRXJ5WHR1WHZjQkxQaWljaEIyRzRZZWlmb25KT25nIIEC; bili_jct=cb28d86c76182189a53a0fef09667116; DedeUserID=10915224; DedeUserID__ckMd5=392b599eb4a19036; sid=8efdl57c; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzMwOTc4OTUsImlhdCI6MTczMjgzODYzNSwicGx0IjotMX0.t0JDkwXn0WSUHikiMU_i6IocKfNKGz1N29-KZvVdPag; bili_ticket_expires=1733097835; bp_t_offset_10915224=1005029571398991872; b_lsid=EE73D8B9_19376D80F52"
    }

    def __init__(self):
        """
        初始化方法
        """
        # 初始化mongodb数据库的客户端和要存入的集合
        self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017')
        self.collection = self.mongo_client['Comment']['bilibili']

    @staticmethod
    def json_change(next_offset):
        """对next_offset内容的转换函数
        next_offset是请求下一页评论时必须携带在请求参数里的内容，
        但因为在当前页获取到的其值不是最终在请求参数里的合法形式，
        所以需要用这个函数做个转换
        """
        # 将原始 JSON 字符串嵌套到新的 JSON 对象中
        result = {"offset": next_offset}
        # 序列化最终结果
        final_output = json.dumps(result)
        # 返回转换后的json字符串
        return final_output

    def get_wrid(self, wts, is_first, next_offset=None):
        """
        模拟js获取加密参数w_rid的函数
        w_rid参数是请求时必须携带上的加密参数，
        经过js逆向分析，找到了其加密的逻辑，使用这个函数模拟出来

        :param wts: 当前时间戳
        :param is_first: 是否为第一页
        :param next_offset: 下一页的偏移量
        :return: 加密后的w_rid参数
        """
        # 将获取的next_offset转换为可以携带在请求参数里的形式
        next_offset = self.json_change(next_offset)
        # 根据是否为第一页，构造不同的加密所需的参数列表
        # 第一页的加密所需参数列表
        if is_first:
            l = [
                "mode=2",
                "oid=1056417986",
                "pagination_str=%7B%22offset%22%3A%22%22%7D",
                "plat=1",
                "seek_rpid=",
                "type=1",
                "web_location=1315875",
                f"wts={wts}",
            ]
        # 非第一页的加密所需参数列表
        else:
            l = [
                "mode=2",
                "oid=1056417986",
                f"pagination_str={quote(next_offset)}",
                "plat=1",
                "type=1",
                "web_location=1315875",
                f"wts={wts}",
            ]

        # 将参数列表连接成字符串
        y = "&".join(l)
        # 加密使用的密钥: 经过测试，这个值是一个固定的值
        a = "ea1db124af3c7062474693fa704f4ff8"
        # 使用MD5加密生成w_rid加密参数并返回
        w_rid = hashlib.md5((y + a).encode("utf-8")).hexdigest()
        return w_rid


    def get_params(self, is_first, next_offset=None):
        """
        生成请求参数字典

        :param is_first: 是否为第一页
        :param next_offset: 下一页的偏移量
        :return: 请求参数字典
        """
        # 获取当前时间戳
        wts = int(time.time())
        # 根据时间戳、是否为第一页和下一页偏移量生成加密参数w_rid
        w_rid = self.get_wrid(wts, is_first, next_offset)
        # 将next_offset转换为可以携带在请求参数里的形式
        next_offset = self.json_change(next_offset)
        # 根据是否为第一页，构造不同的参数字典
        if is_first:
            # 第一页的请求参数字典
            params = {
                "oid": "1056417986",
                "type": "1",
                "mode": "2",
                "pagination_str": '{"offset":""}',
                "plat": "1",
                "seek_rpid": "",
                "web_location": "1315875",
                "w_rid": f"{w_rid}",
                "wts": f"{wts}",
            }
        else:
            # 非第一页的请求参数字典
            params = {
                "oid": "1056417986",
                "type": "1",
                "mode": "2",
                "pagination_str": next_offset,
                "plat": "1",
                "web_location": "1315875",
                "w_rid": f"{w_rid}",
                "wts": f"{wts}",
            }

        # 返回请求参数字典
        return params

    def save_data(self, json_data):
        """
        将获取的评论信息存入mongodb数据库

        :param json_data: 包含评论信息的JSON数据
        """
        # 遍历JSON数据中的每条评论
        for reply in json_data['data']['replies']:
            # 初始化一个空字典来存储评论信息
            data = {}
            # 提取评论者的昵称
            data['nick_name'] = reply["member"]["uname"]
            # 提取评论者的性别
            data['sex'] = reply["member"]["sex"]
            # 提取评论者的位置信息，并去除前缀
            data['location'] = reply['reply_control']['location'].replace('IP属地：', '')
            # 提取评论的内容
            data['comment'] = reply["content"]["message"]
            # 将评论信息存入mongodb数据库
            self.collection.insert_one(data)


    def get_data(self, page_num):
        """
        获取指定页数的评论数据，并将其存入数据库

        该方法通过发送GET请求获取评论数据，并将获取的数据存入MongoDB数据库。
        该方法需要指定页数作为参数，会根据页数发送相应数量的GET请求。

        :param page_num: 需要获取的评论页数
        :return: None
        """
        # 获取第一页的评论数据
        # 首先，获取第一页的请求参数
        params = self.get_params(is_first=True)
        # 发送GET请求获取第一页的评论数据
        response = requests.get(self.url, headers=self.headers, params=params, cookies=self.cookies, verify=False)
        # 将获取的数据转换为JSON格式
        json_data = response.json()
        # 将获取的评论数据存入数据库
        self.save_data(json_data)
        # 获取下一页的偏移量
        next_offset = json_data['data']['cursor']['pagination_reply']['next_offset']

        # 获取剩余页数的评论数据
        # 通过循环发送GET请求获取剩余页数的评论数据
        for _ in range(page_num - 1):
            # 获取下一页的请求参数
            params = self.get_params(is_first=False, next_offset=next_offset)
            # 发送GET请求获取下一页的评论数据
            response = requests.get(self.url, headers=self.headers, params=params, cookies=self.cookies, verify=False)
            # 将获取的数据转换为JSON格式
            json_data = response.json()
            # 将获取的评论数据存入数据库
            self.save_data(json_data)
            # 获取下一页的偏移量
            next_offset = json_data['data']['cursor']['pagination_reply']['next_offset']


    def run(self):
        """
        启动爬虫的入口方法
        """
        # 开始爬取评论，可以指定爬取的评论页数
        self.get_data(10)
        # 爬取结束后关闭数据库连接
        self.mongo_client.close()

if __name__ == '__main__':
    spider = BiliBiliSpider()
    spider.run()

