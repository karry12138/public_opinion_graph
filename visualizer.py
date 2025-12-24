"""
知识图谱可视化模块
"""
from neo4j import GraphDatabase
import config
from typing import Dict, List
import json


class GraphVisualizer:
    """图谱可视化工具"""
    
    def __init__(self):
        """初始化连接"""
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
    
    def close(self):
        """关闭连接"""
        self.driver.close()
    
    def get_event_summary(self) -> Dict:
        """获取事件摘要"""
        with self.driver.session() as session:
            query = """
            MATCH (e:Event)
            OPTIONAL MATCH (e)-[:处于]->(p:OpinionPhase)
            OPTIONAL MATCH (o:Organization)-[:发布]->(e)
            RETURN e.content as content, 
                   e.event_type as event_type,
                   e.comment_count as comment_count,
                   e.reply_count as reply_count,
                   p.phase as phase,
                   o.name as organization
            LIMIT 1
            """
            result = session.run(query)
            record = result.single()
            
            if record:
                return {
                    'content': record['content'],
                    'event_type': record['event_type'],
                    'comment_count': record['comment_count'],
                    'reply_count': record['reply_count'],
                    'opinion_phase': record['phase'],
                    'organization': record['organization']
                }
            return {}
    
    def get_sentiment_distribution(self) -> Dict:
        """获取情感分布"""
        with self.driver.session() as session:
            query = """
            MATCH (c:Comment)
            RETURN c.sentiment as sentiment, count(*) as count
            ORDER BY count DESC
            """
            result = session.run(query)
            
            distribution = {}
            for record in result:
                distribution[record['sentiment']] = record['count']
            
            return distribution
    
    def get_top_demands(self, limit: int = 10) -> List[Dict]:
        """获取主要诉求"""
        with self.driver.session() as session:
            query = """
            MATCH (d:Demand)<-[:提出]-(u:User)
            RETURN d.content as demand, 
                   d.frequency as frequency,
                   count(u) as user_count
            ORDER BY user_count DESC
            LIMIT $limit
            """
            result = session.run(query, limit=limit)
            
            demands = []
            for record in result:
                demands.append({
                    'demand': record['demand'],
                    'frequency': record['frequency'],
                    'user_count': record['user_count']
                })
            
            return demands
    
    def get_solutions(self) -> Dict:
        """获取解决方案"""
        with self.driver.session() as session:
            query = """
            MATCH (s:Solution)
            RETURN s.type as type, s.content as content
            ORDER BY s.type
            """
            result = session.run(query)
            
            solutions = {
                '已采取措施': [],
                '建议方案': []
            }
            
            for record in result:
                sol_type = record['type']
                content = record['content']
                
                if sol_type in solutions:
                    solutions[sol_type].append(content)
            
            return solutions
    
    def get_user_interaction_network(self, limit: int = 20) -> Dict:
        """获取用户互动网络"""
        with self.driver.session() as session:
            query = """
            MATCH (u1:User)-[:发表]->(r:Reply)-[:回复]->(c:Comment)<-[:发表]-(u2:User)
            RETURN u1.name as from_user, 
                   u2.name as to_user, 
                   count(*) as interaction_count
            ORDER BY interaction_count DESC
            LIMIT $limit
            """
            result = session.run(query, limit=limit)
            
            interactions = []
            for record in result:
                interactions.append({
                    'from': record['from_user'],
                    'to': record['to_user'],
                    'count': record['interaction_count']
                })
            
            return {'interactions': interactions}
    
    def get_negative_comments(self, limit: int = 10) -> List[Dict]:
        """获取负面评论"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User)-[:发表]->(c:Comment)
            WHERE c.sentiment = '负面'
            RETURN u.name as author,
                   c.content as content,
                   c.emotion as emotion,
                   c.intensity as intensity,
                   c.time as time
            ORDER BY c.intensity DESC
            LIMIT $limit
            """
            result = session.run(query, limit=limit)
            
            comments = []
            for record in result:
                comments.append({
                    'author': record['author'],
                    'content': record['content'],
                    'emotion': record['emotion'],
                    'intensity': record['intensity'],
                    'time': record['time']
                })
            
            return comments
    
    def generate_report(self) -> str:
        """生成分析报告"""
        report = []
        report.append("="*70)
        report.append("舆情分析报告")
        report.append("="*70)
        
        # 事件摘要
        event = self.get_event_summary()
        if event:
            report.append("\n【事件概况】")
            report.append(f"发布方: {event.get('organization', '未知')}")
            report.append(f"事件类型: {event.get('event_type', '未知')}")
            report.append(f"内容: {event.get('content', '')[:100]}...")
            report.append(f"评论数: {event.get('comment_count', 0)}")
            report.append(f"回复数: {event.get('reply_count', 0)}")
            report.append(f"舆论阶段: {event.get('opinion_phase', '未知')}")
        
        # 情感分布
        sentiment = self.get_sentiment_distribution()
        if sentiment:
            report.append("\n【情感分布】")
            total = sum(sentiment.values())
            for sent, count in sentiment.items():
                percentage = (count / total * 100) if total > 0 else 0
                report.append(f"  {sent}: {count} ({percentage:.1f}%)")
        
        # 主要诉求
        demands = self.get_top_demands(5)
        if demands:
            report.append("\n【主要诉求】")
            for i, demand in enumerate(demands, 1):
                report.append(f"  {i}. {demand['demand']}")
                # report.append(f"     频率: {demand['frequency']}, 提及用户数: {demand['user_count']}")
                report.append(f"     提及用户数: {demand['user_count']}")
        
        # 解决方案
        solutions = self.get_solutions()
        if solutions.get('已采取措施'):
            report.append("\n【已采取措施】")
            for i, action in enumerate(solutions['已采取措施'], 1):
                report.append(f"  {i}. {action}")
        
        if solutions.get('建议方案'):
            report.append("\n【建议解决方案】")
            for i, suggestion in enumerate(solutions['建议方案'], 1):
                report.append(f"  {i}. {suggestion}")
        
        # 负面评论样例
        negative = self.get_negative_comments(3)
        if negative:
            report.append("\n【典型负面评论】")
            for i, comment in enumerate(negative, 1):
                report.append(f"  {i}. 作者: {comment['author']}")
                report.append(f"     情绪: {comment['emotion']} (强度: {comment['intensity']})")
                report.append(f"     内容: {comment['content'][:80]}...")
        
        report.append("\n" + "="*70)
        
        return "\n".join(report)
    
    def export_graph_data(self, output_file: str = "output/graph_data.json"):
        """导出图谱数据为JSON"""
        data = {
            'event_summary': self.get_event_summary(),
            'sentiment_distribution': self.get_sentiment_distribution(),
            'top_demands': self.get_top_demands(10),
            'solutions': self.get_solutions(),
            'user_interactions': self.get_user_interaction_network(20),
            'negative_comments': self.get_negative_comments(10)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"图谱数据已导出到: {output_file}")
        return data
    
    def print_cypher_queries(self):
        """打印常用的Cypher查询语句"""
        queries = [
            ("查看所有节点与关系(限制关系上限400条)","MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 400"),
            ("查看所有节点类型", "MATCH (n) RETURN DISTINCT labels(n) as node_type, count(*) as count"),
            ("查看事件及其关系", "MATCH (e:Event)-[r]->(n) RETURN e, r, n LIMIT 50"),
            ("查看负面评论", "MATCH (c:Comment) WHERE c.sentiment = '负面' RETURN c LIMIT 20"),
            ("查看用户诉求", "MATCH (u:User)-[:提出]->(d:Demand) RETURN u.name, d.content LIMIT 20"),
            ("查看舆论阶段", "MATCH (e:Event)-[:处于]->(p:OpinionPhase) RETURN e.content, p.phase, p.reason"),
            ("查看评论网络", "MATCH (u:User)-[:发表]->(c:Comment)-[:评论]->(e:Event) RETURN u, c, e LIMIT 30"),
            ("查看官方回应", "MATCH (o:Organization)-[:发表]->(r:Reply) RETURN o.name, r.content, r.time LIMIT 20"),
            ("查看高强度情感", "MATCH (c:Comment) WHERE c.intensity >= 8 RETURN c.author, c.content, c.emotion, c.intensity")
        ]
        
        print("\n" + "="*70)
        print("常用Cypher查询语句")
        print("="*70)
        
        for title, query in queries:
            print(f"\n// {title}")
            print(query)
            print()


if __name__ == "__main__":
    visualizer = GraphVisualizer()
    
    try:
        # 生成报告
        print(visualizer.generate_report())
        
        # 导出数据
        print("\n正在导出图谱数据...")
        visualizer.export_graph_data()
        
        # 打印查询语句
        visualizer.print_cypher_queries()
        
    except Exception as e:
        print(f"错误: {e}")
        print("提示: 请确保Neo4j已启动且已运行过 main_pipeline.py 构建图谱")
    finally:
        visualizer.close()

