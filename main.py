"""
xhs-scraper Quick Start Script
验证 Cookie 配置是否正确
"""

import asyncio
from xhs_scraper import XHSClient


async def main():
    # 替换为你的 Cookie 值
    cookies = {"a1": "your_a1_value", "web_session": "your_web_session_value"}

    async with XHSClient(cookies=cookies, rate_limit=2.0) as client:
        user = await client.users.get_self_info()
        print("登录成功！")
        print(f"昵称: {user.nickname}")


if __name__ == "__main__":
    asyncio.run(main())
