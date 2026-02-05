import requests
from typing import List, Dict, Any

class Researcher:
    def __init__(self, config: Dict[str, Any]):
        """
        适配 config.yaml 中 deep_research 节点的初始化
        """
        # 获取深度搜索配置
        dr_config = config.get("deep_research", {})
        
        self.enabled = dr_config.get("enabled", False)
        self.api_key = dr_config.get("api_key")
        # 直接从配置读取触发关键词，如果没有则使用默认值
        self.trigger_keywords = dr_config.get("trigger_keywords", ["AI", "人寿", "保险", "理赔", "寿险"])
        self.max_results = dr_config.get("max_results", 3)
        
        if self.enabled and self.api_key:
            print(f"✅ [Researcher] 初始化成功。监控关键词: {self.trigger_keywords}")
        else:
            print("⚠️ [Researcher] 未启用或缺少 API Key。")

    def search_and_research(self, query: str) -> str:
        """
        调用 Tavily 获取深度内容摘要
        """
        if not self.enabled or not self.api_key:
            return ""

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True,  # 核心：获取 Tavily 自动生成的简报
            "max_results": self.max_results
        }

        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # 优先返回智能回答 (answer 字段)
            answer = data.get("answer")
            if answer:
                return answer
            
            # 如果没有直接回答，返回结果摘要
            results = data.get("results", [])
            if results:
                return " | ".join([r.get('content', '')[:100] for r in results[:2]])
            
            return ""
        except Exception as e:
            print(f"❌ [Tavily] 搜索异常: {e}")
            return ""
