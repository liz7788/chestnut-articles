"""
方格子標題同步檢查器
比對 articles.txt 標題與方格子實際發布標題，找出不一致的文章。
用法：
  python -X utf8 sync_titles.py          # 檢查模式（只列差異）
  python -X utf8 sync_titles.py --fix    # 自動修正 articles.txt + 重新生成導流站
"""
import os
import re
import sys
import time
import random
import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_FILE = os.path.join(SCRIPT_DIR, "articles.txt")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def load_articles():
    """從 articles.txt 讀取文章列表，保留行號"""
    articles = []
    with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            raw = line.rstrip("\n")
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if " | " in stripped:
                title, url = stripped.rsplit(" | ", 1)
                articles.append({
                    "line_num": i,
                    "title": title.strip(),
                    "url": url.strip(),
                    "raw": raw,
                })
    return articles


def fetch_title(url, retries=3):
    """從方格子文章頁面抓取實際標題"""
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 403:
                wait = (attempt + 1) * 5
                print(f"  ⚠️ 403 被擋，等 {wait} 秒後重試...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            # 優先用 og:title（最乾淨）
            og = soup.find("meta", property="og:title")
            if og and og.get("content"):
                return og["content"].strip()
            # 備用：<title> 標籤（可能有後綴）
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
                # 移除方格子常見後綴
                title = re.sub(r"\s*[-–—|]\s*方格子.*$", "", title)
                return title
            return None
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep(3)
            else:
                print(f"  ❌ 抓取失敗: {e}")
                return None
    return None


def apply_fixes(diffs):
    """將差異寫回 articles.txt"""
    with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for d in diffs:
        idx = d["line_num"] - 1
        old_line = lines[idx]
        # 替換標題部分，保留 URL
        new_line = old_line.replace(d["local_title"], d["vocus_title"], 1)
        lines[idx] = new_line

    with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\n✅ 已更新 {len(diffs)} 筆標題到 articles.txt")


def regenerate_site():
    """呼叫 generate_site.py 重新生成導流站"""
    import subprocess
    result = subprocess.run(
        [sys.executable, os.path.join(SCRIPT_DIR, "generate_site.py")],
        capture_output=True, text=True, cwd=SCRIPT_DIR
    )
    if result.returncode == 0:
        print("✅ 導流站已重新生成（index.html + sitemap.xml）")
    else:
        print(f"❌ 生成失敗: {result.stderr}")


def main():
    fix_mode = "--fix" in sys.argv

    articles = load_articles()
    total = len(articles)
    print(f"📋 共 {total} 篇文章，開始比對標題...\n")

    diffs = []
    errors = []

    for i, art in enumerate(articles, 1):
        print(f"  [{i}/{total}] {art['title'][:40]}...", end="", flush=True)

        vocus_title = fetch_title(art["url"])

        if vocus_title is None:
            print(" ❌ 抓取失敗")
            errors.append(art)
        elif vocus_title != art["title"]:
            print(" ⚠️ 不一致")
            diffs.append({
                "line_num": art["line_num"],
                "url": art["url"],
                "local_title": art["title"],
                "vocus_title": vocus_title,
            })
        else:
            print(" ✅")

        # 禮貌延遲 2-4 秒
        if i < total:
            time.sleep(random.uniform(2, 4))

    # 結果報告
    print("\n" + "=" * 60)
    print(f"📊 結果：{total} 篇檢查，{len(diffs)} 篇不一致，{len(errors)} 篇抓取失敗")
    print("=" * 60)

    if diffs:
        print("\n⚠️ 標題不一致的文章：\n")
        for j, d in enumerate(diffs, 1):
            print(f"  {j}. Line {d['line_num']}")
            print(f"     導流站：{d['local_title']}")
            print(f"     方格子：{d['vocus_title']}")
            print(f"     URL：{d['url']}")
            print()

        if fix_mode:
            apply_fixes(diffs)
            regenerate_site()
        else:
            print("💡 加 --fix 參數可自動修正：python -X utf8 sync_titles.py --fix")
    else:
        print("\n✅ 所有標題一致，不需要修正。")

    if errors:
        print(f"\n⚠️ {len(errors)} 篇抓取失敗（可能是網路問題，建議稍後重跑）：")
        for e in errors:
            print(f"  - {e['title'][:50]}...")


if __name__ == "__main__":
    main()
