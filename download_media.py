"""
下载小红书笔记的媒体文件
Download media files from a Xiaohongshu note
"""

import asyncio
from pathlib import Path
from xhs_scraper import XHSClient
from xhs_scraper.utils import download_media

# ========== 配置区域 / Configuration ==========
COOKIES = {
    "a1": "在这里粘贴你的a1值",  # Paste your a1 here
    "web_session": "在这里粘贴你的web_session值",  # Paste your web_session here
}

NOTE_ID = "7397841456987897348"  # 笔记ID / Note ID
XSEC_TOKEN = ""  # 从笔记链接中获取的xsec_token / xsec_token from note link
OUTPUT_DIR = "downloads"  # 下载目录 / Download directory
# ========== 配置结束 / End Configuration ==========


async def main():
    """
    主函数：获取笔记并下载所有媒体文件
    Main function: fetch note and download all media files
    """
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    async with XHSClient(cookies=COOKIES) as client:
        print(f"正在获取笔记: {NOTE_ID}")
        print(f"Getting note: {NOTE_ID}")
        print("-" * 50)

        # 获取笔记详情 / Fetch note details
        note = await client.notes.get_note(
            note_id=NOTE_ID,
            xsec_token=XSEC_TOKEN,
        )

        if not note:
            print("笔记获取失败 / Failed to fetch note")
            return

        print(f"笔记标题 / Note Title: {note.title}")
        print(f"笔记类型 / Note Type: {note.type}")
        print(f"媒体数量 / Media Count: {len(note.images)}")
        print("-" * 50)

        if not note.images:
            print("笔记中没有媒体文件 / No media files in note")
            return

        # 下载媒体文件 / Download media files
        print(f"开始下载媒体文件到: {OUTPUT_DIR}")
        print(f"Starting download media files to: {OUTPUT_DIR}")

        try:
            paths = await download_media(
                urls=note.images,
                output_dir=OUTPUT_DIR,
                filename_pattern="{note_id}_{index}.{ext}",
                note_id=note.note_id,
            )

            print("-" * 50)
            print(f"下载完成！共下载 {len(paths)} 个文件")
            print(f"Download completed! {len(paths)} files downloaded")
            print(f"保存位置 / Saved to: {Path(OUTPUT_DIR).resolve()}")

            for i, path in enumerate(paths, 1):
                print(f"  {i}. {Path(path).name}")

        except Exception as e:
            print(f"下载失败 / Download failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
