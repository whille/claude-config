"""
去重模块 - intel skill

两种去重策略：
1. URL 去重：跨源合并相同链接
2. 语义去重：基于标题相似度

参考：Horizon (https://github.com/Thysrael/Horizon)
"""

from urllib.parse import urlparse
from typing import List, Dict, Any
import re


def normalize_url(url: str) -> str:
    """
    标准化 URL 用于去重

    - 去掉 www. 前缀
    - 去掉尾部 /
    - 去掉 #fragment
    - 统一小写域名
    """
    try:
        parsed = urlparse(str(url))
        host = parsed.hostname or ""
        if host.startswith("www."):
            host = host[4:]
        path = parsed.path.rstrip("/")
        return f"{host.lower()}{path}"
    except Exception:
        return url


def dedupe_by_url(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    URL 去重（跨源）

    保留内容最丰富的项，合并来源标签
    """
    url_groups: Dict[str, List[Dict]] = {}

    for item in items:
        key = normalize_url(item.get("url", ""))
        url_groups.setdefault(key, []).append(item)

    merged = []
    for key, group in url_groups.items():
        if len(group) == 1:
            merged.append(group[0])
        else:
            # 按内容丰富度排序（title + summary 长度）
            primary = max(group, key=lambda x: len(x.get("title", "") + x.get("summary", "")))

            # 合并来源
            sources = [item.get("source", "unknown") for item in group]
            primary["merged_sources"] = list(set(sources))

            merged.append(primary)

    return merged


def title_similarity(t1: str, t2: str) -> float:
    """
    简单标题相似度（基于词重叠）

    返回 0.0 - 1.0
    """
    # 提取关键词（去掉停用词）
    stopwords = {"the", "a", "an", "is", "are", "was", "were", "to", "of", "in", "for", "on", "with"}

    def tokenize(text):
        words = re.findall(r"\w+", text.lower())
        return set(w for w in words if w not in stopwords and len(w) > 2)

    words1 = tokenize(t1)
    words2 = tokenize(t2)

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union)


def dedupe_by_title(items: List[Dict[str, Any]], threshold: float = 0.7) -> List[Dict[str, Any]]:
    """
    语义去重（标题相似度）

    Args:
        items: 待去重列表
        threshold: 相似度阈值（0.7 = 70%关键词重叠）
    """
    if len(items) <= 1:
        return items

    unique = []
    for item in items:
        is_dup = False
        for u in unique:
            if title_similarity(item.get("title", ""), u.get("title", "")) > threshold:
                # 发现重复，合并来源
                if "merged_sources" not in u:
                    u["merged_sources"] = [u.get("source", "unknown")]
                u["merged_sources"].append(item.get("source", "unknown"))
                is_dup = True
                break

        if not is_dup:
            unique.append(item)

    return unique


def dedupe_items(items: List[Dict[str, Any]], use_title: bool = False) -> List[Dict[str, Any]]:
    """
    完整去重流程

    1. 先 URL 去重
    2. 可选：再标题去重
    """
    result = dedupe_by_url(items)

    if use_title:
        result = dedupe_by_title(result)

    return result


# 使用示例
if __name__ == "__main__":
    test_items = [
        {"url": "https://www.example.com/article/", "title": "Claude 3.5 Released", "source": "reddit"},
        {"url": "https://example.com/article", "title": "Claude 3.5 Released", "source": "hackernews"},
        {"url": "https://other.com/news", "title": "Claude 3.5 Performance Benchmarks", "source": "bilibili"},
    ]

    deduped = dedupe_items(test_items, use_title=True)

    for item in deduped:
        print(f"[{item.get('source')}] {item.get('title')}")
        if merged := item.get("merged_sources"):
            print(f"  └─ merged from: {merged}")
