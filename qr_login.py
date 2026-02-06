"""
通过扫描二维码登录小红书并获取 Cookie
"""

import asyncio
from xhs_scraper import XHSClient, qr_login
from xhs_scraper.signature import XHShowSignatureProvider
from xhs_scraper.utils.qr_login import QRLoginError


async def main():
    print("正在生成登录二维码...")
    signature_provider = XHShowSignatureProvider()
    cookies = {
        "a1": "PASTE_YOUR_A1_VALUE_HERE",
        "web_session": "PASTE_YOUR_WEB_SESSION_VALUE_HERE",
    }

    if not cookies.get("a1"):
        print("未提供有效的 a1，请先在浏览器登录小红书后重试")
        return

    try:
        cookies = await qr_login(signature_provider, cookies)
    except QRLoginError as exc:
        message = str(exc)
        if "IP存在风险" in message:
            print("接口提示 IP 风险，请切换可靠网络环境后重试。")
            return
        raise

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
