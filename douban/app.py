from flask import Flask, jsonify, request, send_file,render_template
from flask_cors import CORS
import requests
import os
import hashlib
import time

app = Flask(__name__)
CORS(app)

# 简单内存缓存 { cache_key: (timestamp, data) }
CACHE = {}
CACHE_EXPIRE_SECONDS = 3600  # 缓存 1 小时

# 豆瓣API
API_TAG = "https://movie.douban.com/j/search_subjects"

def get_cache_key(tag, rating, page, keyword):
    return f"{tag}_{rating}_{page}_{keyword}"

def get_from_cache(key):
    item = CACHE.get(key)
    if item:
        timestamp, data = item
        if time.time() - timestamp < CACHE_EXPIRE_SECONDS:
            return data
        else:
            del CACHE[key]
    return None

def save_to_cache(key, data):
    CACHE[key] = (time.time(), data)

@app.route("/", methods=["GET"])
def index():
    # 1. 获取参数
    tag = request.args.get("tag", "热门")
    rating = float(request.args.get("rating", 0))
    page = int(request.args.get("page", 0))  # 当前页码，从 0 开始
    page_limit = 20  # 每页 20 条

    # 2. 调用豆瓣接口
    url = API_TAG
    params = {
        "type": "movie",
        "tag": tag,
        "sort": "recommend",
        "page_limit": page_limit,
        "page_start": page * page_limit
    }

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, params=params, headers=headers)
    try:
        movies = r.json().get("subjects", [])
    except Exception:
        movies = []

    # 3. 按评分过滤
    movies = [m for m in movies if float(m.get("rate", 0) or 0) >= rating]

    # 4. 返回模板（或 JSON）
    return render_template(
        "index.html",
        movies=movies,
        tag=tag,
        rating=rating,
        page=page,
        has_next=len(movies) > 0,
    )

@app.route("/api/movies")
def api_movies():
    """异步分页接口，支持 tag 和 keyword 搜索"""
    tag = request.args.get("tag", "热门")
    rating = float(request.args.get("rating", 0))
    page = int(request.args.get("page", 0))
    keyword = request.args.get("keyword", "").strip()
    page_limit = 20

    cache_key = get_cache_key(tag, rating, page, keyword)
    cached = get_from_cache(cache_key)
    if cached:
        return jsonify({"from_cache": True, **cached})

    headers = {"User-Agent": "Mozilla/5.0"}
    # 豆瓣标签筛选 API
    url = API_TAG
    params = {
        "type": "movie",
        "tag": tag,
        "sort": "recommend",
        "page_limit": page_limit,
        "page_start": page * page_limit
    }
    try:
        print(url)
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        # API 格式兼容
        if "subjects" in data:
            movies = data["subjects"]
        elif "items" in data:  # 搜索结果格式不同
            movies = [
                {
                    "title": m.get("title"),
                    "rate": m.get("rating", {}).get("value", 0),
                    "cover": m.get("cover_url"),
                    "url": m.get("url"),
                }
                for m in data["items"]
            ]
        else:
            movies = []
    except Exception as e:
        print("API Error:", e)
        movies = []

    # 评分过滤
    movies = [m for m in movies if float(m.get("rate", 0) or 0) >= rating]

    result = {
        "page": page,
        "movies": movies,
        "has_next": len(movies) > 0
    }

    save_to_cache(cache_key, result)
    return jsonify(result)


@app.route("/proxy_image")
def proxy_image():
    """图片代理 + 本地缓存"""
    image_url = request.args.get("url")
    if not image_url:
        return "Missing URL", 400

    cache_dir = "cache_images"
    os.makedirs(cache_dir, exist_ok=True)
    filename = hashlib.md5(image_url.encode()).hexdigest() + ".jpg"
    filepath = os.path.join(cache_dir, filename)

    if os.path.exists(filepath):
        return send_file(filepath, mimetype="image/jpeg")

    try:
        r = requests.get(image_url, timeout=10)
        if r.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(r.content)
            return send_file(filepath, mimetype="image/jpeg")
        else:
            return "Image download failed", 500
    except Exception as e:
        print("Proxy Error:", e)
        return "Proxy Error", 500


if __name__ == "__main__":
    app.run(debug=True)
