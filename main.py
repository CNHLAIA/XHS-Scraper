"""
xhs-scraper Quick Start Script
验证 Cookie 配置是否正确
"""

import asyncio
import os
from xhs_scraper import XHSClient


async def main():
    a1 = os.environ.get("XHS_A1")
    web_session = os.environ.get("XHS_WEB_SESSION")

    if not a1 or not web_session:
        print("请设置环境变量 XHS_A1 和 XHS_WEB_SESSION")
        print("示例:")
        print("  set XHS_A1=your_a1_value")
        print("  set XHS_WEB_SESSION=your_web_session_value")
        return

    cookies = {"a1": a1, "web_session": web_session}

    async with XHSClient(cookies=cookies, rate_limit=2.0) as client:
        user = await client.users.get_self_info()
        print("登录成功！")
        print(f"昵称: {user.nickname}")


if __name__ == "__main__":
    asyncio.run(main())
