"""
获取单条小红书笔记详情
Fetch single Xiaohongshu note details
"""

import asyncio
from xhs_scraper import XHSClient

# ========== 配置区域 / Configuration ==========
COOKIES = {
    "a1": "PASTE_YOUR_A1_VALUE_HERE",  # Paste your a1 here
    "web_session": "PASTE_YOUR_WEB_SESSION_VALUE_HERE",  # Paste your web_session here
}

NOTE_ID = "PASTE_YOUR_NOTE_ID_HERE"  # Paste your note ID here
XSEC_TOKEN = "PASTE_YOUR_XSEC_TOKEN_HERE"  # Paste your xsec_token here
# ========== 配置结束 / End Configuration ==========


async def main():
    async with XHSClient(cookies=COOKIES) as client:
        print(f"正在获取笔记详情: {NOTE_ID}")
        print("-" * 50)

        note = await client.notes.get_note(note_id=NOTE_ID, xsec_token=XSEC_TOKEN)

        # Print note details
        print(f"标题 / Title: {note.title}")
        print(f"描述 / Description: {note.desc}")
        print(f"点赞数 / Likes: {note.liked_count}")
        print(f"评论数 / Comments: {note.commented_count}")
        print(f"分享数 / Shares: {note.shared_count}")
        print(f"图片数 / Image Count: {len(note.images) if note.images else 0}")

        print("-" * 50)
        print("笔记获取成功 / Note fetched successfully")


if __name__ == "__main__":
    asyncio.run(main())
