import datetime

import requests
from core.sqlLiteExec import sqlite_execute





def get_articles_from_oillink(keywords_list: list, page: int, size: int, user_id: int):
    """
    从 OilLink 检索文献，并标记每篇文章是否已被当前用户收藏（is_collected）。
    用 DOI 作为唯一标识匹配 knowledgebase 表。
    """
    url = "http://data.oillink.com/api/shengli/articlesearch/index"
    params = {"keywords": f'{keywords_list}', "page": page, "size": size}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()['data']
        if data is None:
            return []
        for article in data:
            doi = article.get('doi')
            if not doi:
                article['is_collected'] = 0
                continue
            result = sqlite_execute(
                "SELECT COUNT(*) as cnt FROM knowledgebase WHERE mark_info=? AND type_id=1 AND user_id=?",
                (doi, user_id)
            )
            article['is_collected'] = 1 if result and result[0]['cnt'] > 0 else 0
        return data
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return None


def get_patents_from_oillink(query: str, page: int = 0, size: int = 5):
    """
    从 OilLink 检索专利，并标记每篇文章是否已被当前用户收藏（is_collected）。
    用专利ID作为唯一标识匹配 knowledgebase 表。
    """
    url = "http://data.oillink.com/api/shengli/patentsearch/index"
    params = {"query": query, "page": page, "size": size}
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data['code'] != 200:
            return []
        data = data['data']
        new_data = []
        for item in data:
            i = item[0]
            patent_id = i['id']
            id_result = sqlite_execute(
                "SELECT COUNT(*) as cnt FROM knowledgebase WHERE mark_info=? AND type_id=2",
                (patent_id,)
            )
            i['is_collected'] = 1 if id_result and id_result[0]['cnt'] else 0
            if isinstance(i.get('app_date'), dict) and 'seconds' in i['app_date']:
                i['app_date'] = datetime.datetime.fromtimestamp(i['app_date']['seconds'])
            else:
                i['app_date'] = i.get('app_date', '')
            if isinstance(i.get('pub_date'), dict) and 'seconds' in i['pub_date']:
                i['pub_date'] = datetime.datetime.fromtimestamp(i['pub_date']['seconds'])
            else:
                i['pub_date'] = i.get('pub_date', '')
            new_data.append(i)
        return new_data
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return None

if __name__ == '__main__':
    print(get_articles_from_oillink(['computer'], 1, 10, 1))
    print(get_patents_from_oillink('computer', 1, 10))