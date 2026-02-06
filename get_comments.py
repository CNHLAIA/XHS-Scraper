"""
获取笔记评论
Fetch comments from a note
"""

import asyncio
from pathlib import Path
from xhs_scraper import XHSClient
from xhs_scraper.utils import export_to_json, export_to_csv

# ========== 配置区域 / Configuration ==========
COOKIES = {
    "a1": "PASTE_YOUR_A1_VALUE_HERE",  # Paste your a1 here
    "web_session": "PASTE_YOUR_WEB_SESSION_VALUE_HERE",  # Paste your web_session here
}

NOTE_ID = "PASTE_YOUR_NOTE_ID_HERE"  # Note ID to fetch comments from
MAX_PAGES = 5  # 最大爬取页数 / Max pages to scrape
OUTPUT_DIR = "output"  # 输出目录 / Output directory
# ========== 配置结束 / End Configuration ==========


async def main():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    all_comments = []

    async with XHSClient(cookies=COOKIES, rate_limit=2.0) as client:
        print(f"开始获取笔记评论: {NOTE_ID}")
        print(f"最大页数: {MAX_PAGES}")
        print("-" * 50)

        result = await client.comments.get_comments(
            note_id=NOTE_ID,
            max_pages=MAX_PAGES,
        )

        if result.items:
            all_comments.extend(result.items)
            print(f"获取 {len(all_comments)} 条评论")

            # Display sample comments
            print("-" * 50)
            print("样本评论 / Sample Comments:")
            for i, comment in enumerate(result.items[:3], 1):
                print(f"\n评论 {i} / Comment {i}:")
                print(
                    f"  用户 / User: {comment.user.nickname if hasattr(comment, 'user') and hasattr(comment.user, 'nickname') else 'Unknown'}"
                )
                print(
                    f"  内容 / Content: {comment.content[:100] if hasattr(comment, 'content') else 'No content'}"
                )
                if hasattr(comment, "create_time"):
                    print(f"  时间 / Time: {comment.create_time}")
        else:
            print("没有获取到评论 / No comments found")

        print("-" * 50)
        print(f"获取完成！共获取 {len(all_comments)} 条评论")

        if all_comments:
            safe_note_id = NOTE_ID.replace(" ", "_")[:20]
            json_path = f"{OUTPUT_DIR}/comments_{safe_note_id}.json"
            csv_path = f"{OUTPUT_DIR}/comments_{safe_note_id}.csv"

            export_to_json(all_comments, json_path)
            export_to_csv(all_comments, csv_path)

            print(f"已导出到: {json_path}")
            print(f"已导出到: {csv_path}")


if __name__ == "__main__":
    asyncio.run(main())
