import requests
import hashlib
import base64
import urllib.parse
import time
from config import settings



#重庆聚合文献接口
def get_article_from_juhe_api(keywords:list,date:str=None,page=1,size=10,sort=3):
    """
    从重庆聚合文献接口获取文献
    :param keywords: 关键词
    :param date: 查询年份
    :param page: 页码
    :param pagesize: 每页数量
    :return: 文献列表
    """

    def md5_encrypt(text: str) -> str:
        """MD5加密函数"""
        md5 = hashlib.md5()
        md5.update(text.encode('utf-8'))
        return md5.hexdigest()
    exps = []
    for keyword in keywords:
        exps.append(f"关键词:{keyword}")
    if date:
        date = date[5:]
        exps.append(f"年份:{date}")
    exp = " AND ".join(exps)
    exp = urllib.parse.quote(exp)
    params = "{}|{}|{}|{}".format(exp, page, size, sort)
    print('表达式：', urllib.parse.unquote(params))
    times = "{}".format(int(time.time() * 1000))
    en_params = base64.b64encode(params.encode('utf-8')).decode('utf-8')
    sign = "{}|{}|{}".format(en_params, "AF85101E523744ADA233DF14CCC76980", times)
    en_sign = md5_encrypt(sign)
    # 设置请求头
    headers = {
        "User-Agent": "test",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    # 构造请求参数
    query_params = {
        "params": en_params,
        "sign": en_sign,
        "token": "AF85101E523744ADA233DF14CCC76980",
        "times": times
    }
    try:
        # 发送带会话管理的请求
        with requests.Session() as session:
            # 首次请求获取可能的Cookie
            url = "http://61.128.134.70:6655/groups/ask/search"
            session.get(url, headers=headers, params=query_params, timeout=10)

            # 再次请求确保Cookie生效
            response = session.get(url, headers=headers, params=query_params, timeout=10)

            # 输出原始响应内容（用于调试）
            # print("Raw Response:")
            # print(response.text)

            # 检查HTTP状态码
            response.raise_for_status()
            # print("reach here!")
            # 解析JSON响应
            result = response.json()['result']
            # 处理业务逻辑
            paperlist = []
            for record in result['records']:
                paperlist.append(
                    {
                        "标题": f"{record['title']}",
                        "关键词": f"{record['keyword']}",
                        "年份": f"{record['year']}",
                        "摘要": f"{record['content']}",
                        "DOI": f"{record['doi']}",
                        "下载链接": f"http://61.128.134.70:6655{record['full_source']}"
                    }
                )
            return paperlist
    except requests.exceptions.RequestException as e:
        print(f"聚合检索请求发生错误: {str(e)}")
    except ValueError as e:
        print(f"聚合检索JSON解析失败，请检查响应内容是否为有效JSON: {str(e)}")
    except KeyError as e:
        print(f"聚合检索响应数据缺少必要字段: {str(e)}")
    except Exception as e:
        print(f"聚合检索未知错误: {str(e)}")


if __name__ == "__main__":
    print(get_article_from_juhe_api(keywords=['computer'],date='2021-2024', page=1, size=10, sort=3))

