"""
B站 AI 字幕获取模块

获取流程：
1. 调用 subtitle/web/view API 获取 protobuf 格式的字幕信息
2. 从 protobuf 中解析 auth_key
3. 构造字幕 URL: https://aisubtitle.hdslb.com/bfs/ai_subtitle/prod/{aid}{cid}{hash}?auth_key={auth_key}

注意：
- auth_key 有效期约 60 秒
- URL 中的 hash 需要从 protobuf 中提取（解码 URL 编码的路径）
"""

import asyncio
import httpx
import re
import json
from typing import Optional, List, Dict
from dataclasses import dataclass
from urllib.parse import unquote


@dataclass
class BilibiliCredential:
    """B站登录凭证"""
    sessdata: str
    bili_jct: str
    buvid3: str
    dedeuserid: str = ""


@dataclass
class SubtitleItem:
    """字幕条目"""
    time: float
    content: str


class BilibiliAISubtitleFetcher:
    """B站 AI 字幕获取器"""

    def __init__(self, credential: BilibiliCredential):
        self.credential = credential
        self.cookies = {
            "SESSDATA": credential.sessdata,
            "bili_jct": credential.bili_jct,
            "buvid3": credential.buvid3,
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com/",
        }

    def _parse_protobuf_subtitle_url(self, raw_content: bytes) -> Optional[str]:
        """
        从 Protobuf 响应中解析字幕 URL

        Protobuf 结构分析：
        - 包含 ai-zh 语言标识
        - 包含 URL 编码的路径
        - 包含 auth_key 认证密钥

        Returns:
            完整的字幕 URL，如果解析失败返回 None
        """
        raw_str = raw_content.decode('latin-1')

        # 方法1: 直接查找 aisubtitle.hdslb.com URL（最理想）
        url_match = re.search(
            r'(https://aisubtitle\.hdslb\.com/bfs/ai_subtitle/prod/[^\x00-\x20]+)',
            raw_str
        )
        if url_match:
            return url_match.group(1)

        # 方法2: 从 subtitle.bilibili.com 路径解析
        # 路径格式: //subtitle.bilibili.com/{encoded_path}?auth_key={auth_key}
        path_match = re.search(
            r'//subtitle\.bilibili\.com/([^\?]+)\?auth_key=([^\x00-\x20&]+)',
            raw_str
        )

        if path_match:
            encoded_path = path_match.group(1)
            auth_key = path_match.group(2)

            # URL 解码路径
            decoded_path = unquote(encoded_path)

            # 解码后的路径包含某种编码，需要进一步处理
            # 这里需要解码路径中的特殊字符

            return None  # 需要进一步解码

        return None

    def _extract_auth_key(self, raw_content: bytes) -> Optional[str]:
        """从 Protobuf 中提取 auth_key"""
        raw_str = raw_content.decode('latin-1')
        auth_match = re.search(r'auth_key=([^\x00-\x20&]+)', raw_str)
        return auth_match.group(1) if auth_match else None

    async def get_video_info(self, bvid: str) -> Dict:
        """获取视频基本信息"""
        async with httpx.AsyncClient() as client:
            url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            resp = await client.get(url, cookies=self.cookies, headers=self.headers)
            data = resp.json()

            if data.get('code') != 0:
                raise ValueError(f"获取视频信息失败: {data.get('message')}")

            return {
                'aid': data['data']['aid'],
                'cid': data['data']['cid'],
                'title': data['data']['title'],
                'duration': data['data']['duration'],
                'owner': data['data']['owner']['name'],
            }

    async def get_subtitle_protobuf(self, aid: int, cid: int) -> bytes:
        """获取字幕信息的 Protobuf 数据"""
        async with httpx.AsyncClient(cookies=self.cookies, headers=self.headers) as client:
            url = "https://api.bilibili.com/x/v2/subtitle/web/view"
            params = {
                'oid': cid,
                'pid': aid,
                'context_ext': '{"video_type":1}',
                'cur_production_type': 0,
                'type': 1,
            }
            resp = await client.get(url, params=params)
            return resp.content

    async def download_subtitle(self, url: str) -> List[SubtitleItem]:
        """下载字幕数据"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)

            if resp.status_code != 200:
                raise ValueError(f"下载字幕失败: HTTP {resp.status_code}")

            data = resp.json()

            if 'body' not in data:
                raise ValueError("字幕数据格式错误")

            return [
                SubtitleItem(
                    time=item.get('from', 0),
                    content=item.get('content', '')
                )
                for item in data['body']
            ]

    async def fetch(self, bvid: str, verbose: bool = True) -> List[SubtitleItem]:
        """
        获取 B站 AI 字幕

        Args:
            bvid: 视频 BV 号
            verbose: 是否打印详细信息

        Returns:
            字幕列表
        """
        # 1. 获取视频信息
        video_info = await self.get_video_info(bvid)
        aid = video_info['aid']
        cid = video_info['cid']

        if verbose:
            print(f"视频: {video_info['title']}")
            print(f"UP主: {video_info['owner']}")
            print(f"时长: {video_info['duration']}秒")

        # 2. 获取 Protobuf 数据
        raw_content = await self.get_subtitle_protobuf(aid, cid)

        if verbose:
            print(f"Protobuf 数据长度: {len(raw_content)} bytes")

        # 3. 解析字幕 URL
        subtitle_url = self._parse_protobuf_subtitle_url(raw_content)

        if not subtitle_url:
            # 提取 auth_key 用于调试
            auth_key = self._extract_auth_key(raw_content)
            if verbose:
                print(f"auth_key: {auth_key}")
            raise ValueError(
                "无法解析字幕 URL。可能原因：\n"
                "1. 该视频没有 AI 字幕\n"
                "2. 字幕 URL 需要特殊解码\n"
                "建议使用浏览器开发者工具抓取完整 URL"
            )

        if verbose:
            print(f"字幕 URL: {subtitle_url[:80]}...")

        # 4. 下载字幕
        return await self.download_subtitle(subtitle_url)

    def to_srt(self, subtitles: List[SubtitleItem]) -> str:
        """转换为 SRT 格式"""
        lines = []
        for i, sub in enumerate(subtitles, 1):
            start_time = self._format_time(sub.time)
            end_time = self._format_time(
                subtitles[i].time if i < len(subtitles) else sub.time + 5
            )
            lines.append(f"{i}")
            lines.append(f"{start_time} --> {end_time}")
            lines.append(sub.content)
            lines.append("")
        return "\n".join(lines)

    def to_plain_text(self, subtitles: List[SubtitleItem]) -> str:
        """转换为纯文本（带时间戳）"""
        return "\n".join(
            f"[{sub.time:.1f}s] {sub.content}" for sub in subtitles
        )

    def to_text_only(self, subtitles: List[SubtitleItem]) -> str:
        """转换为纯文本（不带时间戳）"""
        return "\n".join(sub.content for sub in subtitles)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """格式化时间为 SRT 格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')


def load_credential_from_file(
    filepath: str = "~/.claude/bilibili-credential.json"
) -> BilibiliCredential:
    """从文件加载凭证"""
    import os

    filepath = os.path.expanduser(filepath)
    with open(filepath) as f:
        cred_data = json.load(f)

    return BilibiliCredential(
        sessdata=cred_data['SESSDATA'],
        bili_jct=cred_data['bili_jct'],
        buvid3=cred_data['buvid3'],
        dedeuserid=cred_data.get('DedeUserID', '')
    )


async def fetch_bilibili_ai_subtitle(
    bvid: str,
    credential: BilibiliCredential,
    verbose: bool = True
) -> List[SubtitleItem]:
    """
    获取 B站 AI 字幕的便捷函数

    Args:
        bvid: 视频 BV 号
        credential: B站登录凭证
        verbose: 是否打印详细信息

    Returns:
        字幕列表
    """
    fetcher = BilibiliAISubtitleFetcher(credential)
    return await fetcher.fetch(bvid, verbose=verbose)


async def fetch_with_playwright(
    bvid: str,
    credential: BilibiliCredential,
    verbose: bool = True
) -> List[SubtitleItem]:
    """
    使用 Playwright 获取 B站 AI 字幕（绕过 URL 解码问题）

    通过 Playwright 启动浏览器，监听网络请求，
    捕获 aisubtitle.hdslb.com 的字幕 URL。

    Args:
        bvid: 视频 BV 号
        credential: B站登录凭证
        verbose: 是否打印详细信息

    Returns:
        字幕列表
    """
    from playwright.async_api import async_playwright

    subtitle_url = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # 设置 cookies
        await context.add_cookies([
            {'name': 'SESSDATA', 'value': credential.sessdata, 'domain': '.bilibili.com', 'path': '/'},
            {'name': 'bili_jct', 'value': credential.bili_jct, 'domain': '.bilibili.com', 'path': '/'},
            {'name': 'buvid3', 'value': credential.buvid3, 'domain': '.bilibili.com', 'path': '/'},
        ])

        page = await context.new_page()

        # 监听请求
        def on_request(request):
            nonlocal subtitle_url
            url = request.url
            if 'aisubtitle.hdslb.com' in url and 'auth_key=' in url:
                if verbose:
                    print(f"[捕获] {url[:100]}...")
                subtitle_url = url

        page.on('request', on_request)

        if verbose:
            print(f"访问: https://www.bilibili.com/video/{bvid}/")

        await page.goto(f"https://www.bilibili.com/video/{bvid}/", wait_until='load', timeout=60000)

        # 等待并尝试触发字幕加载
        await asyncio.sleep(5)

        # 点击字幕按钮
        try:
            btn = await page.wait_for_selector('.bpx-player-ctrl-subtitle', timeout=5000)
            if btn is not None:
                await btn.click()
                if verbose:
                    print("点击字幕按钮")
        except Exception:
            pass

        # 等待字幕请求
        await asyncio.sleep(15)

        await browser.close()

    if not subtitle_url:
        raise ValueError("未能捕获字幕 URL，可能该视频没有 AI 字幕")

    # 下载字幕
    async with httpx.AsyncClient() as client:
        resp = await client.get(subtitle_url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": "https://www.bilibili.com/",
        })

        if resp.status_code != 200:
            raise ValueError(f"下载字幕失败: HTTP {resp.status_code}")

        data = resp.json()

        if 'body' not in data:
            raise ValueError("字幕数据格式错误")

        return [
            SubtitleItem(time=item.get('from', 0), content=item.get('content', ''))
            for item in data['body']
        ]


def parse_subtitle_url_from_network(network_log: str) -> Optional[str]:
    """
    从浏览器网络日志中解析字幕 URL

    用户可以在浏览器开发者工具中搜索 "aisubtitle"，
    找到请求后复制 URL，然后使用此函数解析。

    Args:
        network_log: 浏览器网络请求的 URL 或日志

    Returns:
        解析后的字幕 URL
    """
    # 查找 aisubtitle.hdslb.com URL
    match = re.search(
        r'https://aisubtitle\.hdslb\.com/bfs/ai_subtitle/prod/[a-zA-Z0-9]+?\?auth_key=[a-zA-Z0-9\-]+',
        network_log
    )
    return match.group(0) if match else None


# ============ 使用示例 ============

if __name__ == "__main__":
    import asyncio

    async def main():
        # 加载凭证
        credential = load_credential_from_file()

        # 方法1: 使用 Playwright 获取（推荐）
        print("=== 方法1: Playwright 获取 ===")
        try:
            subtitles = await fetch_with_playwright("BV16XdaBaEBh", credential)
            print(f"\n获取到 {len(subtitles)} 条字幕")
            for sub in subtitles[:5]:
                print(f"  [{sub.time:.1f}s] {sub.content}")
        except ValueError as e:
            print(f"错误: {e}")

        # 方法2: 使用便捷函数（需要正确解析 protobuf）
        print("\n=== 方法2: 直接 API 获取 ===")
        try:
            subtitles = await fetch_bilibili_ai_subtitle("BV16XdaBaEBh", credential)
            print(f"\n获取到 {len(subtitles)} 条字幕")
        except ValueError as e:
            print(f"错误: {e}")

        # 方法3: 从浏览器抓取的 URL 直接下载
        # fetcher = BilibiliAISubtitleFetcher(credential)
        # url = "https://aisubtitle.hdslb.com/bfs/ai_subtitle/prod/xxx?auth_key=xxx"
        # subtitles = await fetcher.download_subtitle(url)

    asyncio.run(main())
