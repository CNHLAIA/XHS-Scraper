"""
爬取特定用户的所有笔记
Fetch all notes from a specific user
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

USER_ID = "用户ID"  # User ID to scrape
MAX_PAGES = 10  # 最大爬取页数 / Max pages to scrape
OUTPUT_DIR = "output"  # 输出目录 / Output directory
# ========== 配置结束 / End Configuration ==========


async def main():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    all_notes = []

    async with XHSClient(cookies=COOKIES, rate_limit=2.0) as client:
        print(f"开始获取用户笔记: {USER_ID}")
        print(f"最大页数: {MAX_PAGES}")
        print("-" * 50)

        result = await client.notes.get_user_notes(
            user_id=USER_ID,
            max_pages=MAX_PAGES,
        )

        if result.items:
            all_notes.extend(result.items)
            print(f"获取 {len(result.items)} 篇笔记")
        else:
            print("未获取到任何笔记")

        print("-" * 50)
        print(f"爬取完成！共获取 {len(all_notes)} 篇笔记")

        if all_notes:
            safe_user_id = USER_ID.replace(" ", "_")[:20]
            json_path = f"{OUTPUT_DIR}/user_{safe_user_id}.json"
            csv_path = f"{OUTPUT_DIR}/user_{safe_user_id}.csv"

            export_to_json(all_notes, json_path)
            export_to_csv(all_notes, csv_path)

            print(f"已导出到: {json_path}")
            print(f"已导出到: {csv_path}")


if __name__ == "__main__":
    asyncio.run(main())
