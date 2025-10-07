
import requests
import pprint

API_KEYWORD = "https://movie.douban.com/j/search"



if __name__ == "__main__":
    url = API_KEYWORD
    page = 1
    keyword = "中国"
    params = {
        "query": keyword,
        "start": page * 20,
        "cat": "1002",  # 电影类别
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    data = resp.json()
    pprint.pprint(data)
