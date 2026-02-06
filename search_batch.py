"""
批量搜索爬取小红书笔记
Batch search and scrape Xiaohongshu notes
"""

import asyncio
from pathlib import Path
from xhs_scraper import XHSClient
from xhs_scraper.utils import export_to_json, export_to_csv

# ========== 配置区域 / Configuration ==========
COOKIES = {
    "a1": "在这里粘贴你的a1值",  # Paste your a1 here
    "web_session": "在这里粘贴你的web_session值",  # Paste your web_session here
}

KEYWORD = "露营装备"  # 搜索关键词 / Search keyword
MAX_PAGES = 5  # 最大爬取页数 / Max pages to scrape
SORT = "GENERAL"  # 排序: GENERAL(综合), TIME_DESC(最新), POPULARITY(最热)
NOTE_TYPE = "ALL"  # 类型: ALL(全部), VIDEO(视频), IMAGE(图文)
OUTPUT_DIR = "output"  # 输出目录 / Output directory
# ========== 配置结束 / End Configuration ==========


async def main():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    all_notes = []

    async with XHSClient(cookies=COOKIES, rate_limit=2.0) as client:
        print(f"开始搜索: {KEYWORD}")
        print(f"排序: {SORT}, 类型: {NOTE_TYPE}, 最大页数: {MAX_PAGES}")
        print("-" * 50)

        for page in range(1, MAX_PAGES + 1):
            print(f"正在爬取第 {page}/{MAX_PAGES} 页...")

            result = await client.search.search_notes(
                keyword=KEYWORD,
                page=page,
                sort=SORT,
                note_type=NOTE_TYPE,
            )

            if not result.items:
                print(f"第 {page} 页无结果，停止爬取")
                break

            all_notes.extend(result.items)
            print(f"  获取 {len(result.items)} 篇笔记，累计 {len(all_notes)} 篇")

            if not result.has_more:
                print("没有更多结果")
                break

        print("-" * 50)
        print(f"爬取完成！共获取 {len(all_notes)} 篇笔记")

        if all_notes:
            safe_keyword = KEYWORD.replace(" ", "_")[:20]
            json_path = f"{OUTPUT_DIR}/search_{safe_keyword}.json"
            csv_path = f"{OUTPUT_DIR}/search_{safe_keyword}.csv"

            export_to_json(all_notes, json_path)
            export_to_csv(all_notes, csv_path)

            print(f"已导出到: {json_path}")
            print(f"已导出到: {csv_path}")


if __name__ == "__main__":
    asyncio.run(main())
