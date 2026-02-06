"""
xhs-scraper Quick Start Script
验证 Cookie 配置是否正确
"""

import asyncio
from xhs_scraper import XHSClient


async def main():
    # ⬇️ 把下面的值替换成你自己的 Cookie
    # ⬇️ Replace with your own Cookie values
    cookies = {
        "a1": "在这里粘贴你的a1值",  # Paste your a1 value here
        "web_session": "在这里粘贴你的web_session值",  # Paste your web_session value here
    }

    async with XHSClient(cookies=cookies, rate_limit=2.0) as client:
        user = await client.users.get_self_info()
        print("登录成功！")
        print(f"昵称: {user.nickname}")


if __name__ == "__main__":
    asyncio.run(main())
