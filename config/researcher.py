import requests

class Researcher:
    def __init__(self, config):
        # 从配置文件读取配置
        self.enabled = config.get("enabled", False)
        self.api_key = config.get("api_key", "")
        self.triggers = config.get("trigger_keywords", [])

    def fetch_deep_content(self, title):
        """如果标题匹配，就上网搜深度内容"""
        # 1. 检查是否开启，且标题是否值得搜
        if not self.enabled or not any(word in title for word in self.triggers):
            return ""

        print(f"🔍 发现核心话题：[{title}]，正在上网搜寻深度资料...")
        
        # 2. 调用 Tavily 搜索接口 (这里以 Tavily 为例)
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": f"{title} 深度深度分析 行业影响",
            "search_depth": "advanced",
            "max_results": 2
        }
        
        try:
            response = requests.post(url, json=payload, timeout=15)
            results = response.json().get("results", [])
            # 把搜到的文章正文拼在一起
            context = "\n".join([r.get("content", "") for r in results])
            return f"\n【全网深度补全内容】：\n{context[:2000]}" # 取前2000字防止塞爆
        except:
            return ""
