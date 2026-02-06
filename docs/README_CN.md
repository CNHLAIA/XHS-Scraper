# xhs-scraper - 小红书异步爬虫库

**[English](../README.md)** | **[中文文档](./README_CN.md)**

一个基于 Python 异步特性的高效小红书数据采集工具，支持笔记、用户、评论采集及搜索功能。

## 目录

- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [安装方法](#安装方法)
- [快速开始](#快速开始)
- [Cookie 获取方法](#cookie-获取方法)
- [登录后操作指南](#登录后操作指南)
- [API 详细文档](#api-详细文档)
- [数据模型](#数据模型)
- [数据导出](#数据导出)
- [媒体下载](#媒体下载)
- [错误处理](#错误处理)
- [速率限制](#速率限制)
- [完整示例代码](#完整示例代码)
- [测试](#测试)
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

1. **打开命令行工具**：
   - **Windows**: 按 `Win + R`，输入 `cmd`，按回车
   - **Mac**: 打开"启动台" → 搜索"终端" → 打开

2. **输入以下命令**：
```bash
git clone https://github.com/CNHLAIA/XHS-Scraper.git
cd XHS-Scraper
pip install -e .
```

> 如果提示 `pip` 不存在，请先安装 Python 3.10 或更高版本

## 快速开始

跟着下面的步骤以运行脚本

### 第一步：创建脚本文件

1. **打开项目文件夹**
   - 找到你下载的 `XHS-Scraper` 文件夹
   - 双击打开它

2. **创建新文件**
   - 在文件夹空白处右键 → 新建 → 文本文档
   - 把文件名改成 `my_first_scraper.py`（注意要把 `.txt` 也删掉）
   - 或者用 VS Code、PyCharm 等编辑器直接创建

3. **打开文件并粘贴代码**
   - 双击打开 `my_first_scraper.py`
   - 复制下面的代码粘贴进去：

```python
# my_first_scraper.py
# 这是你的第一个小红书爬虫脚本！

import asyncio
from xhs_scraper import XHSClient

async def main():
    # ⬇️ 把下面的值替换成你自己的 Cookie（参考上面的获取方法）
    cookies = {
        "a1": "在这里粘贴你的a1值",
        "web_session": "在这里粘贴你的web_session值"
    }
    
    async with XHSClient(cookies=cookies, rate_limit=2.0) as client:
        # 获取自己的用户信息，验证 Cookie 是否有效
        user = await client.users.get_self_info()
        print("🎉 登录成功！")
        print(f"你的昵称: {user.nickname}")

if __name__ == "__main__":
     asyncio.run(main())
```

> 可直接运行 `main.py`

### 第二步：运行脚本

1. **打开命令行**
   - Windows: 在项目文件夹中，按住 `Shift` 键，右键空白处 → 选择"在此处打开命令窗口"或"在终端中打开"
   
2. **运行命令**
```bash
python my_first_scraper.py
```

3. **查看结果**
   - 如果看到 `🎉 登录成功！` 和你的昵称，说明一切正常！
   - 如果报错，请检查 Cookie 是否正确复制

## Cookie 获取方法

### 方法一：浏览器开发者工具（最简单，推荐新手使用）

**详细步骤：**

**第 1 步：打开小红书网页版**
- 打开浏览器（Chrome、Edge、Firefox 都可以）
- 在地址栏输入：`https://www.xiaohongshu.com`
- 登录你的小红书账号

**第 2 步：打开开发者工具**
- 按键盘上的 `F12` 键
- 或者：右键点击页面空白处 → 选择"检查"或"Inspect"
- 屏幕右侧或底部会弹出一个新面板

**第 3 步：切换到 Network 标签**
- 在开发者工具顶部找到 `Network`（网络）标签并点击
- 如果看不到，点击 `>>` 或 `...` 展开更多标签

**第 4 步：刷新页面**
- 按 `F5` 或点击浏览器的刷新按钮
- 你会看到 Network 面板中出现很多请求记录

**第 5 步：找到 Cookie**
- 点击列表中的任意一个请求（建议点击第一个）
- 在右侧面板中找到 `Headers`（标头）选项卡
- 向下滚动，找到 `Request Headers`（请求标头）部分
- 找到 `Cookie:` 这一行，它的值很长
- 双击选中整个值，然后 `Ctrl+C` 复制

**第 6 步：提取关键字段**
- 在复制的内容中找到这两个值：
  - `a1=xxxxxxxxx`（a1 等号后面的内容）
  - `web_session=xxxxxxxxx`（web_session 等号后面的内容）
- 把这两个值记下来，后面要用

> ⚠️ **安全警告**：Cookie 包含你的登录凭证，**绝对不要分享给任何人**！

### 方法二：Chrome 自动提取
如果你在 Chrome 浏览器中已登录小红书，可以使用内置工具自动提取：

```python
from xhs_scraper.utils import extract_chrome_cookies

cookies = extract_chrome_cookies()
# 返回的 cookies 可直接传入 XHSClient
```

> 完整脚本见 `chrome_cookies.py`

### 方法三：二维码登录
通过扫描二维码实现自动登录：

```python
from xhs_scraper import qr_login

async def login():
     cookies = await qr_login()
     print(f"获取到的 Cookies: {cookies}")
```

> 完整脚本见 `qr_login.py`

## 登录后操作指南

登录成功后，你可以使用以下功能采集小红书数据。所有示例代码都可以直接复制运行。

### 1. 验证登录状态

首先验证你的 Cookie 是否有效：

```python
import asyncio
from xhs_scraper import XHSClient

async def main():
    cookies = {
        "a1": "在这里粘贴你的a1值",
        "web_session": "在这里粘贴你的web_session值"
    }
    
    async with XHSClient(cookies=cookies) as client:
        user = await client.users.get_self_info()
        print(f"✅ 登录成功！昵称: {user.nickname}")
        print(f"粉丝数: {user.followers}, 关注数: {user.following}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. 采集单篇笔记

通过笔记 ID 和 xsec_token 获取笔记详情：

```python
import asyncio
from xhs_scraper import XHSClient

async def main():
    cookies = {
        "a1": "在这里粘贴你的a1值",
        "web_session": "在这里粘贴你的web_session值"
    }
    
    async with XHSClient(cookies=cookies) as client:
        # note_id 和 xsec_token 可从笔记链接或搜索结果中获取
        note = await client.notes.get_note(
            note_id="笔记ID",
            xsec_token="xsec_token值"
        )
        print(f"标题: {note.title}")
        print(f"内容: {note.desc}")
        print(f"点赞: {note.liked_count}, 评论: {note.commented_count}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. 采集用户的所有笔记

获取指定用户发布的笔记列表：

```python
import asyncio
from xhs_scraper import XHSClient

async def main():
    cookies = {
        "a1": "在这里粘贴你的a1值",
        "web_session": "在这里粘贴你的web_session值"
    }
    
    async with XHSClient(cookies=cookies) as client:
        # 采集前 3 页笔记
        result = await client.notes.get_user_notes(
            user_id="用户ID",
            max_pages=3
        )
        print(f"共获取 {len(result.items)} 篇笔记")
        for note in result.items:
            print(f"- {note.title}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. 获取用户信息

获取其他用户的主页信息：

```python
import asyncio
from xhs_scraper import XHSClient

async def main():
    cookies = {
        "a1": "在这里粘贴你的a1值",
        "web_session": "在这里粘贴你的web_session值"
    }
    
    async with XHSClient(cookies=cookies) as client:
        user = await client.users.get_user_info(user_id="用户ID")
        print(f"昵称: {user.nickname}")
        print(f"简介: {user.bio}")
        print(f"粉丝: {user.followers}, 关注: {user.following}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 5. 采集笔记评论

获取笔记的评论和子评论：

```python
import asyncio
from xhs_scraper import XHSClient

async def main():
    cookies = {
        "a1": "在这里粘贴你的a1值",
        "web_session": "在这里粘贴你的web_session值"
    }
    
    async with XHSClient(cookies=cookies) as client:
        # 获取一级评论
        comments = await client.comments.get_comments(
            note_id="笔记ID",
            max_pages=2
        )
        print(f"共获取 {len(comments.items)} 条评论")
        
        for comment in comments.items:
            print(f"{comment.user.nickname}: {comment.content}")
            
            # 获取子评论（回复）
            if comment.comment_id:
                sub_comments = await client.comments.get_sub_comments(
                    note_id="笔记ID",
                    root_comment_id=comment.comment_id
                )
                for sub in sub_comments.items:
                    print(f"  └─ {sub.user.nickname}: {sub.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 6. 搜索笔记

通过关键词搜索笔记，支持排序和类型筛选：

```python
import asyncio
from xhs_scraper import XHSClient

async def main():
    cookies = {
        "a1": "在这里粘贴你的a1值",
        "web_session": "在这里粘贴你的web_session值"
    }
    
    async with XHSClient(cookies=cookies) as client:
        # 搜索笔记
        # sort: "GENERAL"(综合), "TIME_DESC"(最新), "POPULARITY"(最热)
        # note_type: "ALL"(全部), "VIDEO"(视频), "IMAGE"(图文)
        result = await client.search.search_notes(
            keyword="露营装备",
            sort="POPULARITY",
            note_type="ALL",
            page=1,
            page_size=20
        )
        
        print(f"搜索到 {len(result.items)} 篇笔记")
        for note in result.items:
            print(f"- {note.title} (点赞: {note.liked_count})")

if __name__ == "__main__":
    asyncio.run(main())
```

### 7. 导出数据

将采集的数据导出为 JSON 或 CSV 格式：

```python
import asyncio
from xhs_scraper import XHSClient
from xhs_scraper.utils import export_to_json, export_to_csv

async def main():
    cookies = {
        "a1": "在这里粘贴你的a1值",
        "web_session": "在这里粘贴你的web_session值"
    }
    
    async with XHSClient(cookies=cookies) as client:
        # 搜索笔记
        result = await client.search.search_notes("美食推荐")
        
        # 导出为 JSON
        export_to_json(result.items, "output/notes.json")
        print("✅ 已导出到 output/notes.json")
        
        # 导出为 CSV（Excel 可直接打开）
        export_to_csv(result.items, "output/notes.csv")
        print("✅ 已导出到 output/notes.csv")

if __name__ == "__main__":
    asyncio.run(main())
```

### 8. 下载图片和视频

下载笔记中的媒体文件：

```python
import asyncio
from xhs_scraper import XHSClient
from xhs_scraper.utils import download_media

async def main():
    cookies = {
        "a1": "在这里粘贴你的a1值",
        "web_session": "在这里粘贴你的web_session值"
    }
    
    async with XHSClient(cookies=cookies) as client:
        # 获取笔记详情
        note = await client.notes.get_note(
            note_id="笔记ID",
            xsec_token="xsec_token值"
        )
        
        # 下载图片
        if note.images:
            paths = await download_media(
                urls=note.images,
                output_dir="downloads/",
                filename_pattern="{note_id}_{index}.{ext}",
                note_id=note.note_id
            )
            print(f"✅ 已下载 {len(paths)} 个文件到 downloads/ 目录")

if __name__ == "__main__":
    asyncio.run(main())
```

## 可用脚本

项目提供了多个即用型脚本，无需编写代码即可使用。只需修改脚本顶部的配置区域，然后运行即可。

### 脚本列表

| 脚本名称 | 功能说明 | 配置项 |
|---------|---------|--------|
| `search_batch.py` | 批量搜索爬取笔记，支持多页爬取和自动导出 | KEYWORD, MAX_PAGES, SORT, NOTE_TYPE |
| `get_note.py` | 获取单篇笔记详情 | NOTE_ID, XSEC_TOKEN |
| `get_user_notes.py` | 获取指定用户的所有笔记 | USER_ID, MAX_PAGES |
| `get_user_info.py` | 获取用户主页信息 | USER_ID |
| `get_comments.py` | 获取笔记评论 | NOTE_ID, MAX_PAGES |
| `download_media.py` | 下载笔记中的图片/视频 | NOTE_ID, XSEC_TOKEN, OUTPUT_DIR |

### 使用方法

1. **打开脚本文件**，找到顶部的配置区域：
```python
# ========== 配置区域 / Configuration ==========
COOKIES = {
    "a1": "在这里粘贴你的a1值",
    "web_session": "在这里粘贴你的web_session值",
}
# ... 其他配置项
# ========== 配置结束 / End Configuration ==========
```

2. **填写你的 Cookie** 和其他必要参数

3. **运行脚本**：
```bash
python search_batch.py
```

### 推荐：批量搜索脚本

`search_batch.py` 是最常用的脚本，支持：
- 多页爬取（自动翻页）
- 排序方式选择（综合/最新/最热）
- 笔记类型筛选（全部/视频/图文）
- 自动导出为 JSON 和 CSV 格式

```bash
# 修改配置后直接运行
python search_batch.py
```

## 🧪 测试

本项目包含全面的测试，具有完整的测试覆盖率：

- **195 个测试** 覆盖所有组件
- **100% 通过率** - 所有测试通过 ✅
- **56 个单元测试** 用于独立组件（异常、模型、速率限制器、签名）
- **139 个集成测试** 用于 API 响应、错误处理和客户端初始化
- **完整覆盖** 所有模块和功能

### 快速测试

使用单个命令运行所有测试：

```bash
# 运行所有测试并显示详细输出
python -m pytest tests/ -v

# 预期输出：
# 195 passed in ~11.33s ✅
```

### 运行特定测试

```bash
# 仅运行单元测试
python -m pytest tests/unit/ -v

# 仅运行集成测试
python -m pytest tests/integration/ -v

# 运行特定测试文件
python -m pytest tests/integration/test_api_responses.py -v

# 运行并生成覆盖率报告
python -m pytest tests/ --cov=xhs_scraper --cov-report=html
```

### 测试分类

- **集成测试 (139 个测试)**: API 响应、错误处理、客户端初始化
- **单元测试 (56 个测试)**: 异常、模型、速率限制器、签名验证

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
1. **创建文件**: `get_user_notes.py`
2. **复制内容**:
```python
import asyncio
from xhs_scraper import XHSClient
from xhs_scraper.utils import export_to_json

async def run():
    async with XHSClient(cookies={"a1": "...", "web_session": "..."}) as client:
        # 采集前 3 页笔记
        result = await client.notes.get_user_notes("用户ID", max_pages=3)
        # 结果将保存到项目根目录下的 user_notes.json
        export_to_json(result.items, "user_notes.json")

if __name__ == "__main__":
    asyncio.run(run())
```
3. **如何运行**: `python get_user_notes.py`
4. **输出位置**: 项目根目录下的 `user_notes.json` 文件。

### 示例2：搜索并导出笔记
1. **创建文件**: `search_notes.py`
2. **复制内容**:
```python
import asyncio
from xhs_scraper import XHSClient
from xhs_scraper.utils import export_to_csv

async def run():
    async with XHSClient(cookies={"a1": "...", "web_session": "..."}) as client:
        # 搜索“露营装备”，按热度排序
        search_res = await client.search.search_notes("露营装备", sort="POPULARITY")
        # 结果将保存到项目根目录下的 search_result.csv
        export_to_csv(search_res.items, "search_result.csv")

if __name__ == "__main__":
    asyncio.run(run())
```
3. **如何运行**: `python search_notes.py`
4. **输出位置**: 项目根目录下的 `search_result.csv` 文件。

### 示例3：采集笔记评论
1. **创建文件**: `get_comments.py`
2. **复制内容**:
```python
import asyncio
from xhs_scraper import XHSClient

async def run():
    async with XHSClient(cookies={"a1": "...", "web_session": "..."}) as client:
        note_id = "65xxxxxxxxxxxxxxxx"
        comments = await client.comments.get_comments(note_id, max_pages=2)
        for comment in comments.items:
            print(f"{comment.user.nickname}: {comment.content}")

if __name__ == "__main__":
    asyncio.run(run())
```
3. **如何运行**: `python get_comments.py`
4. **输出位置**: 命令行窗口直接显示结果。

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
