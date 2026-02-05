import requests
from typing import List, Dict, Any

class Researcher:
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("TAVILY_API_KEY")
        self.enabled = config.get("enabled", True)
        self.max_results = config.get("max_results", 3)

    def search_and_research(self, query: str) -> str:
        """调用 Tavily 获取深度背景"""
        if not self.enabled or not self.api_key:
            return ""

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True, # 这是核心：让 Tavily 直接给出总结
            "max_results": self.max_results
        }

        try:
            # 增加超时处理
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # 1. 优先使用 Tavily 生成的智能答案
            answer = data.get("answer")
            if answer:
                return answer

            # 2. 如果没有答案，提取前两个结果的摘要
            results = data.get("results", [])
            if results:
                return " | ".join([r.get('content', '')[:100] for r in results[:2]])
            
            return ""
        except Exception as e:
            print(f"⚠️ Tavily 搜索异常: {e}")
            return ""
