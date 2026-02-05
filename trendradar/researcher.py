import requests
from typing import List, Dict, Any

class Researcher:
    def __init__(self, config: Dict[str, Any]):
        """
        适配你的 config.yaml 结构
        """
        # 1. 提取 deep_research 节点
        dr_config = config.get("deep_research", {})
        
        # 2. 从该节点读取具体配置
        self.enabled = dr_config.get("enabled", False)
        self.api_key = dr_config.get("api_key")
        self.trigger_keywords = dr_config.get("trigger_keywords", ["AI", "人寿", "保险", "理赔", "寿险"])
        self.max_results = dr_config.get("max_results", 3)
        
        print(f"[DEBUG] Researcher 初始化成功: 状态={self.enabled}, Key={self.api_key[:10] if self.api_key else 'None'}...")

    def search_and_research(self, query: str) -> str:
        if not self.enabled or not self.api_key:
            return ""

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True, # 获取 Tavily 自动生成的简报
            "max_results": self.max_results
        }

        try:
            print(f"🔍 [Tavily] 正在深度搜索: {query[:25]}...")
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # 优先返回 Tavily 的智能回答
            answer = data.get("answer")
            if answer:
                return answer
            
            # 备选：返回搜索到的网页内容摘要
            results = data.get("results", [])
            if results:
                return " | ".join([r.get('content', '')[:100] for r in results[:2]])
            
            return ""
        except Exception as e:
            print(f"⚠️ Tavily 请求失败: {e}")
            return ""
