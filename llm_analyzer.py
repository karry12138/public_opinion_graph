"""
LLM分析模块 - 使用通义千问API
"""
from openai import OpenAI
from typing import Dict, List, Any
import json
import config


class LLMAnalyzer:
    """LLM分析器"""
    
    def __init__(self):
        """初始化LLM客户端"""
        config.check_config()
        
        self.client = OpenAI(
            api_key=config.DASHSCOPE_API_KEY,
            base_url=config.DASHSCOPE_BASE_URL
        )
        self.model = config.MODEL_NAME
    
    def _call_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """调用LLM API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的舆情分析助手，擅长分析社交媒体内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM调用错误: {e}")
            return ""
    
    def analyze_topic(self, topic: str, author: str) -> Dict:
        """分析主题内容"""
        prompt = f"""
请分析以下微博内容，提取关键信息。

发布者：{author}
内容：{topic}

请按以下JSON格式返回分析结果（只返回JSON，不要其他内容）：
{{
    "event_type": "事件类型（如：公共交通故障、服务质量问题等）",
    "core_entity": "核心实体（如：地铁5号线）",
    "location": "地点",
    "issue": "主要问题",
    "impact": "影响描述",
    "keywords": ["关键词1", "关键词2", "关键词3"]
}}
"""
        
        result = self._call_llm(prompt, temperature=0.3)
        
        try:
            # 尝试解析JSON
            return json.loads(result)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            return {"raw_response": result}
    
    def analyze_sentiment_batch(self, comments: List[Dict]) -> List[Dict]:
        """批量分析评论情感"""
        results = []
        
        for comment in comments[:20]:  # 限制处理数量以节省API调用
            main_comment = comment.get('main_comment', {})
            content = main_comment.get('content', '')
            author = main_comment.get('author', '')
            
            if not content:
                continue
            
            sentiment = self.analyze_sentiment(content)
            
            results.append({
                'author': author,
                'content': content,
                'sentiment': sentiment['sentiment'],
                'reason': sentiment.get('reason', ''),
                'demands': sentiment.get('demands', [])
            })
        
        return results
    
    def analyze_sentiment(self, comment: str) -> Dict:
        """分析单条评论的情感"""
        prompt = f"""
请分析以下评论的情感倾向和潜在诉求。

评论内容：{comment}

请按以下JSON格式返回（只返回JSON）：
{{
    "sentiment": "正面/负面/中性",
    "emotion": "具体情绪（如：不满、愤怒、理解、讽刺、询问等）",
    "intensity": "情感强度（1-10）",
    "reason": "判断理由",
    "demands": ["提取的诉求1", "提取的诉求2"]
}}
"""
        
        result = self._call_llm(prompt, temperature=0.3)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "sentiment": "中性",
                "emotion": "未知",
                "intensity": 5,
                "reason": result,
                "demands": []
            }
    
    def judge_opinion_phase(self, event_info: Dict, stats: Dict, 
                           time_span: Dict, official_responses: List[Dict],
                           sentiment_summary: Dict) -> Dict:
        """判断舆论发展周期"""
        prompt = f"""
请根据以下信息判断该舆情事件目前处于哪个发展阶段。

**事件信息：**
- 内容：{event_info.get('topic_content', '')}
- 评论数：{stats.get('total_comment_groups', 0)}
- 回复数：{stats.get('total_replies', 0)}

**时间跨度：**
- 开始时间：{time_span.get('start', '')}
- 结束时间：{time_span.get('end', '')}
- 持续天数：{time_span.get('span_days', 0)}

**官方回应：**
- 回应次数：{len(official_responses)}
- 是否有回应：{'是' if official_responses else '否'}

**情感分布：**
{json.dumps(sentiment_summary, ensure_ascii=False, indent=2)}

**舆论发展周期定义：**
- 潜伏期：事件刚发生，信息发布
- 爆发期：大量评论涌现，情绪激烈
- 发酵期：话题扩散，讨论深化
- 消退期：官方回应后，关注度下降
- 平息期：事件结束

请按以下JSON格式返回（只返回JSON）：
{{
    "phase": "潜伏期/爆发期/发酵期/消退期/平息期",
    "confidence": "判断置信度（1-10）",
    "reason": "判断理由",
    "characteristics": ["特征1", "特征2", "特征3"],
    "trend": "发展趋势预测"
}}
"""
        
        result = self._call_llm(prompt, temperature=0.5)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "phase": "未知",
                "confidence": 5,
                "reason": result,
                "characteristics": [],
                "trend": "未知"
            }
    
    def extract_solutions(self, event_info: Dict, comments: List[Dict], 
                         official_responses: List[Dict]) -> Dict:
        """提取解决方案和建议"""
        # 构建评论摘要
        comment_summary = "\n".join([
            f"- {c.get('main_comment', {}).get('content', '')[:100]}"
            for c in comments[:10]
        ])
        
        official_summary = "\n".join([
            f"- {r.get('content', '')[:100]}"
            for r in official_responses[:5]
        ])
        
        prompt = f"""
基于以下舆情事件信息，提取解决方案和改进建议。

**事件内容：**
{event_info.get('topic_content', '')}

**公众主要评论：**
{comment_summary}

**官方回应：**
{official_summary if official_summary else "暂无"}

请按以下JSON格式返回（只返回JSON）：
{{
    "taken_actions": ["已采取的措施1", "已采取的措施2"],
    "unmet_demands": ["未满足的诉求1", "未满足的诉求2"],
    "suggested_solutions": ["建议方案1", "建议方案2", "建议方案3"],
    "risk_assessment": "风险评估",
    "priority_actions": ["优先处理事项1", "优先处理事项2"]
}}
"""
        
        result = self._call_llm(prompt, temperature=0.7)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "taken_actions": [],
                "unmet_demands": [],
                "suggested_solutions": [],
                "risk_assessment": result,
                "priority_actions": []
            }
    
    def extract_key_demands(self, comments: List[Dict]) -> Dict:
        """提取关键诉求统计"""
        comment_texts = [
            c.get('main_comment', {}).get('content', '')
            for c in comments[:30]
        ]
        
        all_comments = "\n".join([f"{i+1}. {text}" for i, text in enumerate(comment_texts) if text])
        
        prompt = f"""
请分析以下评论，统计和归纳公众的主要诉求。

评论内容：
{all_comments}

请按以下JSON格式返回（只返回JSON）：
{{
    "main_demands": [
        {{
            "demand": "诉求内容",
            "frequency": "提及频率（高/中/低）",
            "urgency": "紧急程度（1-10）"
        }}
    ],
    "demand_summary": "诉求总结"
}}
"""
        
        result = self._call_llm(prompt, temperature=0.5)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "main_demands": [],
                "demand_summary": result
            }


if __name__ == "__main__":
    # 测试代码
    from data_parser import WeiboDataParser
    
    print("初始化分析器...")
    analyzer = LLMAnalyzer()
    parser = WeiboDataParser("weibo_comments_full.json")
    
    print("\n=== 分析主题 ===")
    event_info = parser.extract_event_info()
    topic_analysis = analyzer.analyze_topic(
        event_info['topic_content'],
        event_info['author']
    )
    print(json.dumps(topic_analysis, ensure_ascii=False, indent=2))
    
    print("\n=== 情感分析 ===")
    comments = parser.extract_comments(limit=5)
    sentiment_results = analyzer.analyze_sentiment_batch(comments)
    for result in sentiment_results:
        print(f"作者: {result['author']}")
        print(f"情感: {result['sentiment']}")
        print(f"内容: {result['content'][:50]}...")
        print()

