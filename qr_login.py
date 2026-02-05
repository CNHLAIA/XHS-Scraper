"""
通过扫描二维码登录小红书并获取 Cookie
"""

import asyncio
from xhs_scraper import XHSClient, qr_login


async def main():
    print("正在生成登录二维码...")
    cookies = await qr_login()

    if not cookies:
        print("登录失败或超时")
        return

    print("登录成功！")
    print(f"a1: {cookies.get('a1', '')}")
    print(f"web_session: {cookies.get('web_session', '')}")

    # 验证 Cookie
    async with XHSClient(cookies=cookies, rate_limit=2.0) as client:
        user = await client.users.get_self_info()
        print(f"验证成功！昵称: {user.nickname}")


if __name__ == "__main__":
    asyncio.run(main())
