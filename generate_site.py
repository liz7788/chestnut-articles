"""
方格子 SEO 導流站生成器
讀取 articles.txt，自動生成 index.html + sitemap.xml
用法：python generate_site.py
"""
import os
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_FILE = os.path.join(SCRIPT_DIR, "articles.txt")
OUTPUT_DIR = SCRIPT_DIR


def load_articles():
    """從 articles.txt 讀取文章列表"""
    articles = []
    with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if " | " in line:
                title, url = line.rsplit(" | ", 1)
                articles.append({"title": title.strip(), "url": url.strip()})
    return articles


def categorize(articles):
    """把文章分類"""
    categories = {}
    for a in articles:
        title = a["title"]
        if any(k in title for k in ["行動電源", "行充", "mAh"]):
            cat = "行動電源"
        elif any(k in title for k in ["充電器", "GaN", "氮化鎵"]):
            cat = "充電器"
        elif any(k in title for k in ["無線充電", "充電板", "充電座"]):
            cat = "無線充電"
        elif any(k in title for k in ["香氛", "擴香", "蠟燭", "精油", "水氧機"]):
            cat = "香氛擴香"
        elif any(k in title for k in ["嬰兒", "監視器", "攝影機"]):
            cat = "嬰兒監控"
        elif any(k in title for k in ["網卡", "SIM", "eSIM"]):
            cat = "日本旅遊"
        elif any(k in title for k in ["儲能", "露營"]):
            cat = "戶外電源"
        elif any(k in title for k in ["洗衣機"]):
            cat = "家電"
        else:
            cat = "其他好物"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(a)
    return categories


def generate_html(articles, categories):
    """生成 index.html"""
    today = datetime.now().strftime("%Y-%m-%d")

    # 生成分類區塊
    cat_sections = ""
    for cat, items in categories.items():
        links = ""
        for a in items:
            links += f'<li><a href="{a["url"]}" target="_blank" rel="noopener">{a["title"]}</a></li>\n'
        cat_sections += f"""
    <section>
      <h2>{cat}</h2>
      <ul>
{links}      </ul>
    </section>
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>栗子小姐姐｜2026 好物推薦總整理</title>
  <meta name="description" content="栗子小姐姐的方格子文章總整理，行動電源、充電器、香氛擴香、嬰兒監視器等 2026 年最新推薦評比，幫你快速找到需要的好物。">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://liz7788.github.io/chestnut-articles/">
  <meta property="og:title" content="栗子小姐姐｜2026 好物推薦總整理">
  <meta property="og:description" content="行動電源、充電器、香氛擴香、嬰兒監視器等 2026 年最新推薦評比">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://liz7788.github.io/chestnut-articles/">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.7; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background: #fafafa; }}
    h1 {{ font-size: 1.6em; margin-bottom: 8px; color: #1a1a1a; }}
    .subtitle {{ color: #666; margin-bottom: 30px; font-size: 0.95em; }}
    h2 {{ font-size: 1.2em; margin: 25px 0 10px; padding: 8px 12px; background: #fff; border-left: 4px solid #4a90d9; border-radius: 4px; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ margin: 6px 0; }}
    a {{ color: #4a90d9; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    section {{ margin-bottom: 15px; }}
    .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 0.85em; }}
  </style>
</head>
<body>
  <h1>栗子小姐姐｜好物推薦總整理</h1>
  <p class="subtitle">所有文章都在<a href="https://vocus.cc/salon/liz0821">方格子 vocus</a>，這裡是快速導覽。共 {len(articles)} 篇文章，持續更新中。</p>
{cat_sections}
  <div class="footer">
    <p>最後更新：{today}｜所有文章發布在<a href="https://vocus.cc/salon/liz0821">方格子 vocus</a></p>
  </div>
</body>
</html>"""

    output_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html 已生成（{len(articles)} 篇文章）")


def generate_sitemap(articles):
    """生成 sitemap.xml"""
    today = datetime.now().strftime("%Y-%m-%d")

    urls = f"""  <url>
    <loc>https://liz7788.github.io/chestnut-articles/</loc>
    <lastmod>{today}</lastmod>
    <priority>1.0</priority>
  </url>
"""
    for a in articles:
        urls += f"""  <url>
    <loc>{a['url']}</loc>
    <lastmod>{today}</lastmod>
    <priority>0.8</priority>
  </url>
"""

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}</urlset>"""

    output_path = os.path.join(OUTPUT_DIR, "sitemap.xml")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"sitemap.xml 已生成（{len(articles) + 1} 個 URL）")


if __name__ == "__main__":
    articles = load_articles()
    if not articles:
        print("articles.txt 裡沒有文章，請先新增")
        exit(1)
    categories = categorize(articles)
    generate_html(articles, categories)
    generate_sitemap(articles)
    print("完成！接下來跑 git add . && git commit && git push 就會自動更新")
