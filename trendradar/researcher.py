import requests
import json
from typing import List, Dict, Any

class Researcher:
    def __init__(self, config: Dict[str, Any]):
        """
        初始化研究员模块 (Tavily 增强版)
        """
        self.config = config
        # 从配置中读取 Tavily API Key
        self.api_key = config.get("TAVILY_API_KEY") or config.get("api_key")
        self.enabled = config.get("enabled", True)
        self.search_depth = config.get("search_depth", "basic")
        self.max_results = config.get("max_results", 3)
        
        # 关心的关键词（用于热榜过滤，RSS建议全量或宽泛匹配）
        self.keywords = ["人工智能", "安全", "渗透", "漏洞","AI", "人寿", "保险", "理赔", "寿险"]

    def search_and_research(self, query: str) -> str:
        """
        核心方法：通过 Tavily 搜索并返回增强背景
        """
        if not self.enabled or not self.api_key:
            return ""

        # 简单的关键词预校验（可选：如果你希望只搜特定内容）
        # if not any(k.lower() in query.lower() for k in self.keywords):
        #     return ""

        print(f"🔍 Tavily 正在深度调研: {query}...")
        
        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": self.search_depth,
            "include_answer": True,  # 让 Tavily 直接给出一个简短答案
            "max_results": self.max_results
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # 优先提取 Tavily 的智能回答
            answer = data.get("answer")
            if answer:
                return f"[智能摘要]: {answer}"

            # 如果没有直接回答，则拼接前几个搜索结果的描述
            results = data.get("results", [])
            if not results:
                return ""
                
            snippets = []
            for i, res in enumerate(results[:2]):
                snippets.append(f"{res.get('content', '')[:150]}...")
            
            return " | ".join(snippets)

        except Exception as e:
            print(f"❌ Tavily 搜索请求出错: {str(e)}")
            return ""

    def fetch_deep_content(self, title: str) -> str:
        """兼容旧版调用的别名"""
        return self.search_and_research(title)
