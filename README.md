概述

该项目实现了一个用于爬取 B 站《黑神话悟空》最终预告视频最新评论的爬虫脚本，抓取评论信息包括：

    发布者昵称
    性别
    IP 属地
    评论内容

爬取的数据会存储在本地的 MongoDB 数据库中。
功能

    评论爬取：
        爬取视频下的多页评论内容。
        支持动态加密参数生成，模拟 JavaScript 的加密逻辑。

    数据存储：
        通过 pymongo 存储爬取的评论信息到 MongoDB 数据库中。

    支持分页：
        自动抓取多页评论，并提取下一页的偏移量实现翻页爬取。

依赖项

运行该脚本需要以下 Python 库：

    requests：用于发送 HTTP 请求。
    pymongo：用于与 MongoDB 数据库交互。
    urllib3：支持 HTTPS 请求。
    hashlib：生成 MD5 加密参数。
    time：用于生成时间戳。

您可以通过以下命令安装依赖：

pip install requests pymongo

配置说明
必要配置

    MongoDB：
        数据存储使用 MongoDB，默认连接 mongodb://localhost:27017。
        数据存储在 Comment 数据库的 bilibili 集合中。
        确保本地 MongoDB 服务已启动。

    Cookies：
        cookies 字段中包含用户的登录信息，用于绕过登录限制。
        脚本中的 cookies 是静态值，需要定期更新以避免过期。

API 地址

爬取的评论 API：

https://api.bilibili.com/x/v2/reply/wbi/main

使用方法

    确保 MongoDB 服务运行正常：

sudo service mongod start

运行脚本：

python bilibili.py

数据存储：

    爬取的评论会自动存入 MongoDB，您可以通过 MongoDB 客户端查询数据：

        mongo
        use Comment
        db.bilibili.find()

代码结构

    类名：BiliBiliSpider
        主要功能包括参数生成、评论数据获取与存储。
    主要方法：
        get_params：生成 API 所需的动态参数（包括加密参数 w_rid）。
        save_data：将评论数据存入 MongoDB。
        get_data：根据指定页数获取评论数据。
        run：启动爬虫任务，爬取多页评论。

注意事项

    Cookie 有效性：
        由于 B 站的接口需要登录，cookies 中的 SESSDATA 等信息可能会过期。
        如果爬取失败，请更新 cookies 内容。

    IP 封禁风险：
        频繁发送请求可能会导致 IP 被封禁。建议设置合理的请求间隔或使用代理。

    法律合规：
        请确保爬取的内容仅用于学习研究，遵守 B 站用户协议及相关法律法规。

示例输出

存储的评论数据示例如下：

{
    "nick_name": "示例昵称",
    "sex": "男",
    "location": "广东",
    "comment": "真期待这款游戏！"
}

扩展方向

    代理支持：
        添加代理池以减少 IP 封禁的风险。

    分页自动化：
        动态调整页数以爬取最新数据。

    多线程优化：
        使用多线程或异步编程提高爬取效率。