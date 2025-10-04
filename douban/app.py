import os
import requests
from flask import Flask, request, Response, render_template
from flask_cors import CORS
from urllib.parse import unquote, urlparse

app = Flask(__name__)
CORS(app)
DOUBAN_API = "https://movie.douban.com/j/search_subjects"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# 缓存目录
CACHE_DIR = os.path.join("static", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

@app.route("/proxy_image")
def proxy_image():
    url = request.args.get("url")
    if not url:
        return "Missing url", 400

    # 解码 URL
    url = unquote(url)

    # 取 URL 最后的文件名作为缓存名
    filename = os.path.basename(urlparse(url).path)
    cache_path = os.path.join(CACHE_DIR, filename)

    # 如果缓存存在，直接返回
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return Response(f.read(), content_type="image/jpeg")

    try:
        r = requests.get(url, stream=True, headers=headers, timeout=10)
        r.raise_for_status()

        # 保存到本地缓存
        with open(cache_path, "wb") as f:
            f.write(r.content)

        return Response(r.content, content_type=r.headers.get("Content-Type", "image/jpeg"))
    except Exception as e:
        return f"Error fetching image: {e}", 500



@app.route("/", methods=["GET", "POST"])
def index():
    movies = []
    if request.method == "POST":
        tag = request.form.get("tag", "热门")
        page_str = request.form.get("page", "").strip()
        min_rate_str = request.form.get("min_rate", "").strip()

        # 页码默认 0
        page = int(page_str) if page_str.isdigit() else 0
        # 评分下限默认 0
        try:
            min_rate = float(min_rate_str) if min_rate_str else 0
        except ValueError:
            min_rate = 0

        params = {
            "type": "movie",
            "tag": tag,
            "page_limit": 20,
            "page_start": page * 20,
        }
        try:
            resp = requests.get(DOUBAN_API, params=params, headers=headers, timeout=5)
            # print(resp.text[:200])
            data = resp.json()
            movies = data.get("subjects", [])
            # pprint.pprint(movies)
            # 过滤评分
            movies = [m for m in movies if m.get("rate") and float(m["rate"]) >= min_rate]
        except Exception as e:
            print("API Error:", e)

    return render_template("index.html", movies=movies)

if __name__ == "__main__":
    app.run(debug=True)
