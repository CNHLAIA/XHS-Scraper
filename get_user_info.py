"""
获取小红书用户信息
Get Xiaohongshu user profile information
"""

import asyncio
from xhs_scraper import XHSClient

# ========== 配置区域 / Configuration ==========
COOKIES = {
    "a1": "19b5fc9739cwk6zaa3t0i5mf5jz5tkezqt744vaiw50000300915",
    "web_session": "040069b4dec4f41cf7a78be6b13b4b95249354",
}

USER_ID = "58aab4a182ec3907ed364cfc"  # 要获取的用户ID / User ID to fetch
# ========== 配置结束 / End Configuration ==========


async def main():
    """
    获取并打印用户信息
    Fetch and print user profile information
    """
    async with XHSClient(cookies=COOKIES) as client:
        print(f"正在获取用户信息...")
        print(f"Fetching user information...")
        print("-" * 50)

        try:
            # 获取用户信息 / Fetch user info
            user = await client.users.get_user_info(user_id=USER_ID)

            # 打印用户详情 / Print user details
            print(f"昵称 / Nickname: {user.nickname}")
            print(f"用户ID / User ID: {user.user_id}")
            print(f"个签 / Bio: {user.bio}")
            print(f"粉丝数 / Followers: {user.followers}")
            print(f"关注数 / Following: {user.following}")
            print(f"头像 / Avatar: {user.avatar}")

            print("-" * 50)
            print(f"用户信息获取成功！")
            print(f"User information fetched successfully!")

        except Exception as e:
            print(f"获取失败 / Failed to fetch: {str(e)}")
            print(f"请检查USER_ID和COOKIES是否正确")
            print(f"Please check if USER_ID and COOKIES are correct")


if __name__ == "__main__":
    asyncio.run(main())
