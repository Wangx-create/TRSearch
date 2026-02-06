import re
from html.parser import HTMLParser
from typing import Dict, List

import requests

class Researcher:
    def __init__(self, config):
        # 从配置文件读取配置
        self.enabled = config.get("enabled", False)
        self.api_key = config.get("api_key", "")
        self.triggers = config.get("trigger_keywords", [])
        self.max_results = config.get("max_results", 3)
        self.search_depth = config.get("search_depth", "advanced")
        self.timeout = config.get("timeout", 15)

    def _should_trigger(self, query: str) -> bool:
        if not self.enabled or not self.api_key:
            return False
        if not self.triggers:
            return True
        return any(word in query for word in self.triggers)

    def search_news(self, query: str, include_url: bool = True, max_results: int = None) -> List[Dict]:
        """搜索全网新闻并返回结果列表"""
        if not self._should_trigger(query):
            return []

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": self.search_depth,
            "max_results": max_results or self.max_results,
            "include_raw_content": True,
        }
        if include_url:
            payload["include_urls"] = True

        response = requests.post("https://api.tavily.com/search", json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])

    def read_article(self, url: str) -> str:
        """读取文章正文"""
        if not url:
            return ""

        if self.api_key:
            try:
                payload = {"api_key": self.api_key, "url": url}
                response = requests.post("https://api.tavily.com/extract", json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                content = data.get("content") or data.get("raw_content") or ""
                if content:
                    return content
            except requests.RequestException:
                pass

        try:
            response = requests.get(url, timeout=self.timeout, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            return self._strip_html(response.text)
        except requests.RequestException:
            return ""

    def _strip_html(self, html: str) -> str:
        class _Extractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.parts = []

            def handle_data(self, data):
                cleaned = data.strip()
                if cleaned:
                    self.parts.append(cleaned)

        parser = _Extractor()
        parser.feed(html)
        text = " ".join(parser.parts)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def fetch_deep_content(self, title):
        """如果标题匹配，就上网搜深度内容"""
        # 1. 检查是否开启，且标题是否值得搜
        if not self._should_trigger(title):
            print("匹配失败")
            return ""

        print(f"🔍 发现核心话题：[{title}]，正在上网搜寻深度资料...")
        
        try:
            response = requests.post(url, json=payload, timeout=15)
            results = response.json().get("results", [])
            # 把搜到的文章正文拼在一起
            context = "\n".join([r.get("content", "") for r in results])
            return f"\n【全网深度补全内容】：\n{context[:2000]}" # 取前2000字防止塞爆
        except:
            results = self.search_news(query=f"{title} 深度分析 行业影响", include_url=True)
            contents = []
            for result in results:
                url = result.get("url", "")
                content = result.get("raw_content") or result.get("content", "")
                if url:
                    article_text = self.read_article(url)
                    if article_text:
                        content = article_text
                if content:
                    contents.append(content)
            context = "\n".join(contents)
            if not context:
                return ""
            return f"\n【全网深度补全内容】：\n{context[:2000]}"
        except requests.RequestException:
            return ""
