"""
微博数据解析模块
"""
import json
from datetime import datetime
from typing import Dict, List, Any
import re


class WeiboDataParser:
    """微博数据解析器"""
    
    def __init__(self, json_file_path: str):
        """初始化解析器"""
        self.json_file_path = json_file_path
        self.data = None
        
    def load_data(self) -> Dict:
        """加载JSON数据"""
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        return self.data
    
    def extract_event_info(self) -> Dict:
        """提取事件基本信息"""
        if not self.data:
            self.load_data()
            
        topic = self.data.get('topic', '')
        
        # 使用正则提取关键信息
        event_info = {
            'url': self.data.get('url', ''),
            'author': self.data.get('topic_author', ''),
            'topic_content': topic,
            'comment_count': self.data.get('comment_groups_count', 0),
            'reply_count': self.data.get('total_replies', 0),
            'groups_with_replies': self.data.get('groups_with_replies', 0)
        }
        
        # 尝试提取结构化信息
        event_info['extracted_info'] = self._extract_structured_info(topic)
        
        return event_info
    
    def _extract_structured_info(self, topic: str) -> Dict:
        """从主题中提取结构化信息"""
        info = {
            'line': None,
            'location': None,
            'issue': None,
            'impact_time': None
        }
        
        # 提取线路（如：5号线）
        line_match = re.search(r'(\d+号线)', topic)
        if line_match:
            info['line'] = line_match.group(1)
        
        # 提取位置（如：莘庄至北桥）
        location_match = re.search(r'([\u4e00-\u9fa5]+至[\u4e00-\u9fa5]+)', topic)
        if location_match:
            info['location'] = location_match.group(1)
        
        # 提取故障类型
        issue_keywords = ['车辆故障', '信号故障', '设备故障', '人员受伤']
        for keyword in issue_keywords:
            if keyword in topic:
                info['issue'] = keyword
                break
        
        # 提取影响时间
        time_match = re.search(r'(\d+分钟)', topic)
        if time_match:
            info['impact_time'] = time_match.group(1)
        
        return info
    
    def extract_comments(self, limit: int = None) -> List[Dict]:
        """提取评论数据"""
        if not self.data:
            self.load_data()
        
        comment_groups = self.data.get('comment_groups', [])
        
        if limit:
            comment_groups = comment_groups[:limit]
        
        parsed_comments = []
        
        for group in comment_groups:
            main_comment = group.get('main_comment', {})
            replies = group.get('replies', [])
            
            comment_data = {
                'index': group.get('index'),
                'main_comment': {
                    'author': main_comment.get('author', ''),
                    'content': main_comment.get('content', ''),
                    'time': main_comment.get('time', ''),
                    'source': main_comment.get('source', ''),
                    'user_id': main_comment.get('user_id', '')
                },
                'replies': [
                    {
                        'author': reply.get('author', ''),
                        'content': reply.get('content', ''),
                        'time': reply.get('time', ''),
                        'source': reply.get('source', '')
                    }
                    for reply in replies
                ],
                'has_replies': group.get('has_replies', False),
                'reply_count': len(replies)
            }
            
            parsed_comments.append(comment_data)
        
        return parsed_comments
    
    def get_time_span(self) -> Dict:
        """获取评论时间跨度"""
        if not self.data:
            self.load_data()
        
        comment_groups = self.data.get('comment_groups', [])
        
        times = []
        for group in comment_groups:
            main_comment = group.get('main_comment', {})
            if main_comment.get('time'):
                times.append(main_comment['time'])
            
            for reply in group.get('replies', []):
                if reply.get('time'):
                    times.append(reply['time'])
        
        if not times:
            return {'start': None, 'end': None, 'span_days': 0}
        
        # 简单的时间排序（基于字符串）
        times_sorted = sorted(times)
        
        return {
            'start': times_sorted[0],
            'end': times_sorted[-1],
            'span_days': self._calculate_day_span(times_sorted[0], times_sorted[-1])
        }
    
    def _calculate_day_span(self, start_time: str, end_time: str) -> int:
        """计算时间跨度（天数）"""
        try:
            # 假设时间格式为 "25-11-13 07:52"
            start = datetime.strptime(start_time.split()[0], "%y-%m-%d")
            end = datetime.strptime(end_time.split()[0], "%y-%m-%d")
            return (end - start).days
        except:
            return 0
    
    def get_official_responses(self) -> List[Dict]:
        """提取官方回应"""
        if not self.data:
            self.load_data()
        
        official_author = self.data.get('topic_author', '')
        official_responses = []
        
        comment_groups = self.data.get('comment_groups', [])
        
        for group in comment_groups:
            for reply in group.get('replies', []):
                if reply.get('author') == official_author:
                    official_responses.append({
                        'content': reply.get('content', ''),
                        'time': reply.get('time', ''),
                        'responding_to': group.get('main_comment', {}).get('author', '')
                    })
        
        return official_responses
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if not self.data:
            self.load_data()
        
        comment_groups = self.data.get('comment_groups', [])
        
        total_comments = len(comment_groups)
        total_replies = sum(len(group.get('replies', [])) for group in comment_groups)
        
        return {
            'total_comment_groups': total_comments,
            'total_replies': total_replies,
            'groups_with_replies': self.data.get('groups_with_replies', 0),
            'avg_replies_per_group': total_replies / total_comments if total_comments > 0 else 0
        }


if __name__ == "__main__":
    # 测试代码
    parser = WeiboDataParser("weibo_comments_full.json")
    
    print("=== 事件信息 ===")
    event_info = parser.extract_event_info()
    print(f"作者: {event_info['author']}")
    print(f"主题: {event_info['topic_content']}")
    print(f"提取信息: {event_info['extracted_info']}")
    
    print("\n=== 统计信息 ===")
    stats = parser.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== 时间跨度 ===")
    time_span = parser.get_time_span()
    print(f"开始: {time_span['start']}")
    print(f"结束: {time_span['end']}")
    print(f"跨度: {time_span['span_days']} 天")
    
    print("\n=== 官方回应 ===")
    responses = parser.get_official_responses()
    print(f"官方回应次数: {len(responses)}")
    for i, resp in enumerate(responses[:3], 1):
        print(f"{i}. {resp['content'][:50]}...")

