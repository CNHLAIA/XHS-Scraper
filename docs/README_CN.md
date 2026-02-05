# xhs-scraper - 小红书异步爬虫库

一个基于 Python 异步特性的高效小红书数据采集工具，支持笔记、用户、评论采集及搜索功能。

## 目录

- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [安装方法](#安装方法)
- [快速开始](#快速开始)
- [Cookie 获取方法](#cookie-获取方法)
- [API 详细文档](#api-详细文档)
- [数据模型](#数据模型)
- [数据导出](#数据导出)
- [媒体下载](#媒体下载)
- [错误处理](#错误处理)
- [速率限制](#速率限制)
- [完整示例代码](#完整示例代码)
- [常见问题 FAQ](#常见问题-faq)
- [注意事项](#注意事项)

## 功能特性

- **笔记采集**：支持图文及视频笔记的详细信息采集。
- **用户信息采集**：获取用户个人主页信息、粉丝、关注数等。
- **评论采集**：支持二级评论采集及分页加载。
- **关键词搜索**：支持指定排序方式（综合、最新、最热）和笔记类型（全部、视频、图文）。
- **媒体下载**：支持高清图片和无水印视频下载。
- **数据导出**：内置 JSON 和 CSV 格式导出功能。
- **异步支持**：基于 `httpx` 的全异步实现，高效稳定。
- **速率控制**：内置令牌桶限流算法，保护账号安全。

## 环境要求

- Python >= 3.10
- 核心依赖：
  - `httpx`: 异步 HTTP 客户端
  - `xhshow`: 小红书签名工具
  - `pydantic`: 数据建模与校验
  - `tenacity`: 重试机制

## 安装方法

推荐使用开发模式安装：

```bash
git clone https://github.com/your-repo/xhs-scraper.git
cd xhs-scraper
pip install -e .
```

## 快速开始

以下是一个简单的示例，展示如何初始化客户端并获取用户信息：

```python
import asyncio
from xhs_scraper import XHSClient

async def main():
    # 填入你的 Cookie
    cookies = {
        "a1": "你的 a1 值",
        "web_session": "你的 web_session 值"
    }
    
    # 使用异步上下文管理器初始化客户端
    async with XHSClient(cookies=cookies, rate_limit=2.0) as client:
        # 获取指定用户的信息
        user = await client.users.get_user_info("用户ID")
        print(f"用户昵称: {user.nickname}")
        print(f"粉丝数: {user.followers_count}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Cookie 获取方法

本工具支持多种 Cookie 获取方案：

### 方法一：浏览器开发者工具
1. 打开浏览器登录小红书网页版。
2. 按 `F12` 打开开发者工具，进入 `Network` (网络) 选项卡。
3. 刷新页面，找到任意一个请求，在 `Request Headers` (请求头) 中复制 `Cookie` 字段。
4. 提取关键字段如 `a1` 和 `web_session`。

### 方法二：Chrome 自动提取
如果你在 Chrome 浏览器中已登录小红书，可以使用内置工具自动提取：

```python
from xhs_scraper.utils import extract_chrome_cookies

cookies = extract_chrome_cookies()
# 返回的 cookies 可直接传入 XHSClient
```

### 方法三：二维码登录
通过扫描二维码实现自动登录：

```python
from xhs_scraper import qr_login

async def login():
    cookies = await qr_login()
    print(f"获取到的 Cookies: {cookies}")
```

## API 详细文档

### XHSClient 客户端
主入口类，协调各个 Scraper 模块。

- **初始化参数**:
  - `cookies`: (dict) 小红书 Cookie 字典。
  - `rate_limit`: (float) 每秒最大请求数，默认 2.0。
  - `timeout`: (float) 请求超时时间。

- **属性**:
  - `notes`: `NoteScraper` 实例
  - `users`: `UserScraper` 实例
  - `comments`: `CommentScraper` 实例
  - `search`: `SearchScraper` 实例

### NoteScraper 笔记采集
用于获取笔记详情或用户发布的笔记列表。

- `get_note(note_id, xsec_token) -> NoteResponse`
  - 获取单篇笔记详情。
- `get_user_notes(user_id, cursor="", max_pages=1) -> PaginatedResponse[NoteResponse]`
  - 获取指定用户发布的笔记。

### UserScraper 用户采集
用于获取用户信息。

- `get_user_info(user_id) -> UserResponse`
  - 获取他人主页信息。
- `get_self_info() -> UserResponse`
  - 获取当前登录账号的信息。

### CommentScraper 评论采集
用于获取笔记下的评论信息。

- `get_comments(note_id, cursor="", max_pages=1) -> PaginatedResponse[CommentResponse]`
  - 获取笔记的一级评论。
- `get_sub_comments(note_id, root_comment_id, cursor="") -> PaginatedResponse[CommentResponse]`
  - 获取指定一级评论下的二级评论（子评论）。

### SearchScraper 搜索功能
通过关键词搜索笔记。

- `search_notes(keyword, page=1, page_size=20, sort="GENERAL", note_type="ALL") -> SearchResultResponse`
  - `sort` 可选值: `"GENERAL"` (综合), `"TIME_DESC"` (最新), `"POPULARITY"` (最热)
  - `note_type` 可选值: `"ALL"` (全部), `"VIDEO"` (视频), `"IMAGE"` (图文)

## 数据模型

本项目使用 Pydantic 进行数据校验，主要模型如下：

### UserResponse
- `user_id`: 用户唯一标识
- `nickname`: 昵称
- `avatar`: 头像链接
- `bio`: 个人简介
- `followers`: 粉丝数
- `following`: 关注数

### NoteResponse
- `note_id`: 笔记 ID
- `title`: 标题
- `desc`: 正文内容
- `images`: 图片链接列表
- `video`: 视频信息（如果是视频笔记）
- `user`: 作者信息 (`UserResponse`)
- `liked_count`: 点赞数
- `commented_count`: 评论数
- `shared_count`: 分享数

### CommentResponse
- `comment_id`: 评论 ID
- `content`: 评论内容
- `user`: 评论者信息
- `create_time`: 发布时间
- `sub_comments`: 子评论列表

## 数据导出

### JSON 导出
```python
from xhs_scraper.utils import export_to_json

# data 为模型列表或 PaginatedResponse 对象
export_to_json(notes, "output/notes.json")
```

### CSV 导出
```python
from xhs_scraper.utils import export_to_csv

export_to_csv(notes, "output/notes.csv")
```

## 媒体下载

可以通过以下方式下载笔记关联的媒体资源：

```python
from xhs_scraper.media import download_media

# 自动识别图片或视频并下载到指定目录
await download_media(note, folder="downloads/")
```

## 错误处理

库定义了详细的异常体系，方便捕获和处理：

| 异常类型 | 说明 | 常见 HTTP 状态码 |
|---------|------|-----------------|
| `XHSError` | 所有自定义异常的基类 | - |
| `SignatureError` | API 签名校验失败 | 461 |
| `CaptchaRequiredError` | 触发风控，需要验证码验证 | 471 |
| `CookieExpiredError` | Cookie 已失效或未登录 | 401 / 403 |
| `RateLimitError` | 请求过于频繁 | 429 |
| `APIError` | 通用 API 业务错误 | - |

## 速率限制

本项目内置了基于令牌桶（Token Bucket）算法的限流器。

- **配置**: 在初始化 `XHSClient` 时通过 `rate_limit` 参数控制（单位：请求/秒）。
- **作用**: 自动平滑请求频率，避免因突发大量请求导致被小红书服务器封锁。

## 完整示例代码

### 示例1：采集用户所有笔记
```python
import asyncio
from xhs_scraper import XHSClient
from xhs_scraper.utils import export_to_json

async def run():
    async with XHSClient(cookies={"a1": "...", "web_session": "..."}) as client:
        # 采集前 3 页笔记
        result = await client.notes.get_user_notes("用户ID", max_pages=3)
        export_to_json(result.items, "user_notes.json")

asyncio.run(run())
```

### 示例2：搜索并导出笔记
```python
import asyncio
from xhs_scraper import XHSClient
from xhs_scraper.utils import export_to_csv

async def run():
    async with XHSClient(cookies={...}) as client:
        # 搜索“露营装备”，按热度排序
        search_res = await client.search.search_notes("露营装备", sort="POPULARITY")
        export_to_csv(search_res.items, "search_result.csv")

asyncio.run(run())
```

### 示例3：采集笔记评论
```python
import asyncio
from xhs_scraper import XHSClient

async def run():
    async with XHSClient(cookies={...}) as client:
        note_id = "65xxxxxxxxxxxxxxxx"
        comments = await client.comments.get_comments(note_id, max_pages=2)
        for comment in comments.items:
            print(f"{comment.user.nickname}: {comment.content}")

asyncio.run(run())
```

## 常见问题 FAQ

**Q: 如何获取 xsec_token?**
A: `xsec_token` 通常存在于笔记的分享链接或主页列表的数据包中。在本库中，如果是通过搜索或用户列表获取的笔记对象，通常已自动包含此 Token。

**Q: Cookie 多久过期?**
A: 一般而言，`web_session` 的有效期较短（数天至数周），而 `a1` 相对持久。建议定期检查或使用二维码重新登录。

**Q: 如何避免被封?**
A: 
1. 降低 `rate_limit`（建议 1.0 - 2.0）。
2. 不要长时间、高强度地抓取。
3. 如果遇到 471 错误，请立即停止并手动去浏览器完成验证。

## 注意事项

- **合法使用**：本工具仅供学习和研究使用。请遵守小红书的《使用条款》及相关法律法规。
- **合理采集**：请尊重目标平台的服务器负载，不要进行破坏性的数据采集。
- **隐私保护**：不要泄露获取到的个人隐私数据。
- **免责声明**：作者不对因滥用本工具导致的账号封禁或其他法律责任负责。
