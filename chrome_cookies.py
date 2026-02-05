"""
从 Chrome 浏览器自动提取小红书 Cookie
使用前请确保已在 Chrome 中登录小红书
"""

import asyncio
from xhs_scraper import XHSClient, extract_chrome_cookies


async def main():
    print("正在从 Chrome 提取 Cookie...")
    cookies = extract_chrome_cookies()

    if not cookies:
        print("未找到 Cookie，请确保已在 Chrome 中登录小红书")
        return

    print(f"提取成功: a1={cookies.get('a1', '')[:10]}...")

    # 验证 Cookie 是否有效
    async with XHSClient(cookies=cookies, rate_limit=2.0) as client:
        user = await client.users.get_self_info()
        print(f"验证成功！昵称: {user.nickname}")


if __name__ == "__main__":
    asyncio.run(main())
