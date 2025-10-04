import requests
import json
import time

class DoubanMovieFilter:
    def __init__(self):
        # 豆瓣电影API基础URL
        self.base_url = "https://api.douban.com/v2/movie/search"
        # 请求头，模拟浏览器访问
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def search_movies(self, **kwargs):
        """
        搜索电影
        参数:
            title: 电影标题
            tag: 电影标签/类型
            count: 每页数量
            start: 起始索引
            year_range: 年份范围，如"2010,2020"
        返回:
            电影列表
        """
        params = {
            "apikey": "0b2bdeda43b5955dbef54ca2d59f76d5",  # 公开API密钥
            "count": kwargs.get("count", 20),
            "start": kwargs.get("start", 0)
        }
        
        # 添加可选参数
        if "title" in kwargs:
            params["q"] = kwargs["title"]
        if "tag" in kwargs:
            params["tag"] = kwargs["tag"]
        if "year_range" in kwargs:
            params["year_range"] = kwargs["year_range"]
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("subjects", [])
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return []
        except Exception as e:
            print(f"请求发生错误: {str(e)}")
            return []
    
    def filter_by_rating(self, movies, min_rating=0, max_rating=10):
        """根据评分筛选电影"""
        return [
            movie for movie in movies
            if min_rating <= float(movie["rating"]["average"]) <= max_rating
        ]
    
    def filter_by_year(self, movies, min_year=None, max_year=None):
        """根据年份筛选电影"""
        filtered = []
        for movie in movies:
            year = int(movie["year"])
            if (min_year is None or year >= min_year) and (max_year is None or year <= max_year):
                filtered.append(movie)
        return filtered
    
    def display_movies(self, movies):
        """展示电影信息"""
        if not movies:
            print("没有找到符合条件的电影")
            return
        
        for i, movie in enumerate(movies, 1):
            print(f"\n{i}. {movie['title']} ({movie['year']})")
            print(f"   评分: {movie['rating']['average']}/10")
            print(f"   类型: {', '.join(movie['genres'])}")
            print(f"   导演: {', '.join([d['name'] for d in movie['directors']])}")
            print(f"   主演: {', '.join([c['name'] for c in movie['casts'][:5]])}")  # 只显示前5位主演
            print(f"   豆瓣链接: {movie['alt']}")

if __name__ == "__main__":
    filter_tool = DoubanMovieFilter()
    
    print("豆瓣电影筛选工具")
    print("-" * 30)
    
    # 设置筛选条件
    genre = input("请输入电影类型（如：喜剧、动作，回车表示不限）: ")
    min_rating = float(input("请输入最低评分（0-10，回车表示0）: ") or 0)
    max_rating = float(input("请输入最高评分（0-10，回车表示10）: ") or 10)
    min_year = input("请输入最早年份（如：2010，回车表示不限）: ")
    max_year = input("请输入最晚年份（如：2020，回车表示不限）: ")
    count = int(input("请输入要显示的数量（默认20）: ") or 20)
    
    # 转换年份为整数（如果提供）
    min_year = int(min_year) if min_year else None
    max_year = int(max_year) if max_year else None
    
    print("\n正在搜索符合条件的电影...")
    
    # 搜索电影
    search_params = {
        "tag": genre if genre else None,
        "count": count
    }
    
    # 移除值为None的参数
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    movies = filter_tool.search_movies(** search_params)
    
    # 进一步筛选
    if min_rating > 0 or max_rating < 10:
        movies = filter_tool.filter_by_rating(movies, min_rating, max_rating)
    
    if min_year or max_year:
        movies = filter_tool.filter_by_year(movies, min_year, max_year)
    
    # 显示结果
    print("\n搜索结果：")
    print("-" * 30)
    filter_tool.display_movies(movies)
