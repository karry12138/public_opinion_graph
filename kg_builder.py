"""
Neo4j 知识图谱构建模块
"""
from neo4j import GraphDatabase
from typing import Dict, List, Any
import config
from datetime import datetime


class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self):
        """初始化Neo4j连接"""
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
    
    def close(self):
        """关闭连接"""
        self.driver.close()
    
    def clear_database(self):
        """清空数据库（谨慎使用）"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("数据库已清空")
    
    def create_event_node(self, event_info: Dict, topic_analysis: Dict) -> str:
        """创建事件节点"""
        with self.driver.session() as session:
            query = """
            CREATE (e:Event {
                url: $url,
                author: $author,
                content: $content,
                event_type: $event_type,
                core_entity: $core_entity,
                location: $location,
                issue: $issue,
                impact: $impact,
                comment_count: $comment_count,
                reply_count: $reply_count,
                created_at: datetime()
            })
            RETURN elementId(e) as id
            """
            
            result = session.run(query,
                url=event_info.get('url', ''),
                author=event_info.get('author', ''),
                content=event_info.get('topic_content', ''),
                event_type=topic_analysis.get('event_type', ''),
                core_entity=topic_analysis.get('core_entity', ''),
                location=topic_analysis.get('location', ''),
                issue=topic_analysis.get('issue', ''),
                impact=topic_analysis.get('impact', ''),
                comment_count=event_info.get('comment_count', 0),
                reply_count=event_info.get('reply_count', 0)
            )
            
            event_id = result.single()['id']
            print(f"创建事件节点: {event_id}")
            return event_id
    
    def create_organization_node(self, author: str) -> str:
        """创建组织节点"""
        with self.driver.session() as session:
            query = """
            MERGE (o:Organization {name: $name})
            ON CREATE SET o.type = '官方账号', o.platform = '微博', o.created_at = datetime()
            RETURN elementId(o) as id
            """
            
            result = session.run(query, name=author)
            org_id = result.single()['id']
            return org_id
    
    def create_user_node(self, author: str, location: str = None, user_id: str = None) -> str:
        """创建用户节点"""
        with self.driver.session() as session:
            query = """
            MERGE (u:User {name: $name})
            ON CREATE SET u.location = $location, u.user_id = $user_id, u.created_at = datetime()
            RETURN elementId(u) as id
            """
            
            result = session.run(query, 
                name=author, 
                location=location,
                user_id=user_id
            )
            user_id = result.single()['id']
            return user_id
    
    def create_comment_node(self, comment: Dict, sentiment: Dict = None) -> str:
        """创建评论节点"""
        with self.driver.session() as session:
            main_comment = comment.get('main_comment', {})
            
            query = """
            CREATE (c:Comment {
                author: $author,
                content: $content,
                time: $time,
                source: $source,
                sentiment: $sentiment,
                emotion: $emotion,
                intensity: $intensity,
                created_at: datetime()
            })
            RETURN elementId(c) as id
            """
            
            result = session.run(query,
                author=main_comment.get('author', ''),
                content=main_comment.get('content', ''),
                time=main_comment.get('time', ''),
                source=main_comment.get('source', ''),
                sentiment=sentiment.get('sentiment', '中性') if sentiment else '中性',
                emotion=sentiment.get('emotion', '') if sentiment else '',
                intensity=sentiment.get('intensity', 5) if sentiment else 5
            )
            
            comment_id = result.single()['id']
            return comment_id
    
    def create_reply_node(self, reply: Dict) -> str:
        """创建回复节点"""
        with self.driver.session() as session:
            query = """
            CREATE (r:Reply {
                author: $author,
                content: $content,
                time: $time,
                source: $source,
                created_at: datetime()
            })
            RETURN elementId(r) as id
            """
            
            result = session.run(query,
                author=reply.get('author', ''),
                content=reply.get('content', ''),
                time=reply.get('time', ''),
                source=reply.get('source', '')
            )
            
            reply_id = result.single()['id']
            return reply_id
    
    def create_opinion_phase_node(self, phase_info: Dict) -> str:
        """创建舆论周期节点"""
        with self.driver.session() as session:
            query = """
            CREATE (p:OpinionPhase {
                phase: $phase,
                confidence: $confidence,
                reason: $reason,
                trend: $trend,
                created_at: datetime()
            })
            RETURN elementId(p) as id
            """
            
            result = session.run(query,
                phase=phase_info.get('phase', ''),
                confidence=phase_info.get('confidence', 0),
                reason=phase_info.get('reason', ''),
                trend=phase_info.get('trend', '')
            )
            
            phase_id = result.single()['id']
            return phase_id
    
    def create_demand_node(self, demand: str, status: str = "未知", frequency: str = "未知") -> str:
        """创建诉求节点"""
        with self.driver.session() as session:
            query = """
            MERGE (d:Demand {content: $content})
            ON CREATE SET d.status = $status, d.frequency = $frequency, d.created_at = datetime()
            RETURN elementId(d) as id
            """
            
            result = session.run(query,
                content=demand,
                status=status,
                frequency=frequency
            )
            
            demand_id = result.single()['id']
            return demand_id
    
    def create_solution_node(self, solution: str, type: str = "建议方案") -> str:
        """创建解决方案节点"""
        with self.driver.session() as session:
            query = """
            CREATE (s:Solution {
                content: $content,
                type: $type,
                created_at: datetime()
            })
            RETURN elementId(s) as id
            """
            
            result = session.run(query,
                content=solution,
                type=type
            )
            
            solution_id = result.single()['id']
            return solution_id
    
    def create_relationship(self, from_id: str, to_id: str, rel_type: str, properties: Dict = None):
        """创建关系"""
        with self.driver.session() as session:
            if properties:
                prop_string = ", ".join([f"r.{k} = ${k}" for k in properties.keys()])
                query = f"""
                MATCH (a), (b)
                WHERE elementId(a) = $from_id AND elementId(b) = $to_id
                CREATE (a)-[r:{rel_type}]->(b)
                SET {prop_string}
                RETURN r
                """
                session.run(query, from_id=from_id, to_id=to_id, **properties)
            else:
                query = f"""
                MATCH (a), (b)
                WHERE elementId(a) = $from_id AND elementId(b) = $to_id
                CREATE (a)-[r:{rel_type}]->(b)
                RETURN r
                """
                session.run(query, from_id=from_id, to_id=to_id)
    
    def build_complete_graph(self, analysis_result: Dict):
        """构建完整的知识图谱"""
        print("\n开始构建知识图谱...")
        
        # 1. 创建事件节点
        event_id = self.create_event_node(
            analysis_result['event_info'],
            analysis_result['topic_analysis']
        )
        
        # 2. 创建组织节点
        org_id = self.create_organization_node(
            analysis_result['event_info']['author']
        )
        
        # 3. 创建组织发布事件关系
        self.create_relationship(org_id, event_id, "发布")
        
        # 4. 创建舆论周期节点
        phase_id = self.create_opinion_phase_node(
            analysis_result['opinion_phase']
        )
        self.create_relationship(event_id, phase_id, "处于")
        
        # 5. 创建用户、评论节点和关系
        print("创建评论节点...")
        for i, comment_data in enumerate(analysis_result['comments'][:20]):  # 限制数量
            main_comment = comment_data.get('main_comment', {})
            
            # 创建用户节点
            user_id = self.create_user_node(
                main_comment.get('author', ''),
                main_comment.get('source', ''),
                main_comment.get('user_id', '')
            )
            
            # 查找对应的情感分析结果
            sentiment = None
            for s in analysis_result.get('sentiment_analysis', []):
                if s.get('author') == main_comment.get('author'):
                    sentiment = s
                    break
            
            # 创建评论节点
            comment_id = self.create_comment_node(comment_data, sentiment)
            
            # 创建关系
            self.create_relationship(user_id, comment_id, "发表")
            self.create_relationship(comment_id, event_id, "评论")
            
            # 处理诉求
            if sentiment and sentiment.get('demands'):
                for demand_text in sentiment['demands']:
                    demand_id = self.create_demand_node(demand_text)
                    self.create_relationship(user_id, demand_id, "提出")
                    self.create_relationship(comment_id, demand_id, "包含")
            
            # 处理回复
            for reply_data in comment_data.get('replies', [])[:5]:  # 限制回复数量
                reply_id = self.create_reply_node(reply_data)
                reply_user_id = self.create_user_node(
                    reply_data.get('author', ''),
                    reply_data.get('source', '')
                )
                
                self.create_relationship(reply_user_id, reply_id, "发表")
                self.create_relationship(reply_id, comment_id, "回复")
        
        # 6. 创建解决方案节点
        print("创建解决方案节点...")
        solutions = analysis_result.get('solutions', {})
        
        for action in solutions.get('taken_actions', []):
            solution_id = self.create_solution_node(action, "已采取措施")
            self.create_relationship(org_id, solution_id, "采取")
            self.create_relationship(solution_id, event_id, "针对")
        
        for suggestion in solutions.get('suggested_solutions', []):
            solution_id = self.create_solution_node(suggestion, "建议方案")
            self.create_relationship(solution_id, event_id, "建议针对")
        
        print("\n知识图谱构建完成！")
        print(f"事件节点ID: {event_id}")
    
    def query_graph_stats(self) -> Dict:
        """查询图谱统计信息"""
        with self.driver.session() as session:
            # 节点统计
            node_counts = {}
            labels = ['Event', 'User', 'Comment', 'Reply', 'Organization', 
                     'OpinionPhase', 'Demand', 'Solution']
            
            for label in labels:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                node_counts[label] = result.single()['count']
            
            # 关系统计
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            relationship_count = result.single()['count']
            
            return {
                'nodes': node_counts,
                'relationships': relationship_count,
                'total_nodes': sum(node_counts.values())
            }


if __name__ == "__main__":
    # 测试代码
    kg = KnowledgeGraphBuilder()
    
    print("查询图谱统计...")
    stats = kg.query_graph_stats()
    print(f"\n节点统计:")
    for label, count in stats['nodes'].items():
        print(f"  {label}: {count}")
    print(f"\n总节点数: {stats['total_nodes']}")
    print(f"关系数: {stats['relationships']}")
    
    kg.close()

