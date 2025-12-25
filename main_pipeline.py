"""
主流程Pipeline
"""
import json
from datetime import datetime
from data_parser import WeiboDataParser
from llm_analyzer import LLMAnalyzer
from kg_builder import KnowledgeGraphBuilder


class OpinionAnalysisPipeline:
    """舆情分析Pipeline"""
    
    def __init__(self, json_file_path: str):
        """初始化Pipeline"""
        self.json_file_path = json_file_path
        self.parser = WeiboDataParser(json_file_path)
        self.analyzer = LLMAnalyzer()
        self.kg_builder = KnowledgeGraphBuilder()
        self.analysis_result = {}
    
    def run(self, build_kg: bool = True, clear_db: bool = False):
        """运行完整的分析流程"""
        print("="*60)
        print("舆情分析Pipeline启动")
        print("="*60)
        
        # 步骤1: 数据解析
        print("\n[步骤1] 解析微博数据...")
        self._parse_data()
        
        # 步骤2: LLM分析
        print("\n[步骤2] LLM智能分析...")
        self._analyze_with_llm()
        
        # 步骤3: 保存分析结果
        print("\n[步骤3] 保存分析结果...")
        self._save_results()
        
        # 步骤4: 构建知识图谱
        if build_kg:
            print("\n[步骤4] 构建Neo4j知识图谱...")
            if clear_db:
                confirm = input("确认要清空数据库吗？(yes/no): ")
                if confirm.lower() == 'yes':
                    self.kg_builder.clear_database()
            
            self._build_knowledge_graph()
            
            # 查询统计
            print("\n[步骤5] 查询图谱统计...")
            stats = self.kg_builder.query_graph_stats()
            print(f"\n知识图谱统计:")
            print(f"  总节点数: {stats['total_nodes']}")
            print(f"  总关系数: {stats['relationships']}")
            print(f"\n节点详情:")
            for label, count in stats['nodes'].items():
                if count > 0:
                    print(f"  - {label}: {count}")
        
        print("\n" + "="*60)
        print("Pipeline执行完成！")
        print("="*60)
        
        return self.analysis_result
    
    def _parse_data(self):
        """解析数据"""
        # 提取事件信息
        event_info = self.parser.extract_event_info()
        print(f"  ✓ 事件作者: {event_info['author']}")
        print(f"  ✓ 评论数: {event_info['comment_count']}")
        
        # 提取评论
        comments = self.parser.extract_comments()
        print(f"  ✓ 解析评论组: {len(comments)}")
        
        # 统计信息
        stats = self.parser.get_statistics()
        print(f"  ✓ 总回复数: {stats['total_replies']}")
        
        # 时间跨度
        time_span = self.parser.get_time_span()
        print(f"  ✓ 时间跨度: {time_span['span_days']} 天")
        
        # 官方回应
        official_responses = self.parser.get_official_responses()
        print(f"  ✓ 官方回应: {len(official_responses)} 次")
        
        # 保存到结果
        self.analysis_result.update({
            'event_info': event_info,
            'comments': comments,
            'stats': stats,
            'time_span': time_span,
            'official_responses': official_responses
        })
    
    def _analyze_with_llm(self):
        """使用LLM进行分析"""
        # 1. 分析主题
        print("  → 分析主题内容...")
        topic_analysis = self.analyzer.analyze_topic(
            self.analysis_result['event_info']['topic_content'],
            self.analysis_result['event_info']['author']
        )
        print(f"  ✓ 事件类型: {topic_analysis.get('event_type', '未知')}")
        
        # 2. 情感分析
        print("  → 分析评论情感...")
        sentiment_results = self.analyzer.analyze_sentiment_batch(
            self.analysis_result['comments']
        )
        
        # 统计情感分布
        sentiment_dist = {'正面': 0, '负面': 0, '中性': 0}
        for s in sentiment_results:
            sentiment = s.get('sentiment', '中性')
            sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1
        
        print(f"  ✓ 情感分布: 正面{sentiment_dist['正面']} | "
              f"负面{sentiment_dist['负面']} | 中性{sentiment_dist['中性']}")
        
        # 3. 提取诉求
        print("  → 提取关键诉求...")
        demands = self.analyzer.extract_key_demands(self.analysis_result['comments'])
        print(f"  ✓ 主要诉求数: {len(demands.get('main_demands', []))}")
        
        # 4. 判断舆论周期
        print("  → 判断舆论周期...")
        opinion_phase = self.analyzer.judge_opinion_phase(
            self.analysis_result['event_info'],
            self.analysis_result['stats'],
            self.analysis_result['time_span'],
            self.analysis_result['official_responses'],
            sentiment_dist
        )
        print(f"  ✓ 舆论阶段: {opinion_phase.get('phase', '未知')}")
        
        # 5. 提取解决方案
        print("  → 提取解决方案...")
        solutions = self.analyzer.extract_solutions(
            self.analysis_result['event_info'],
            self.analysis_result['comments'],
            self.analysis_result['official_responses']
        )
        print(f"  ✓ 建议方案数: {len(solutions.get('suggested_solutions', []))}")
        
        # 保存到结果
        self.analysis_result.update({
            'topic_analysis': topic_analysis,
            'sentiment_analysis': sentiment_results,
            'sentiment_distribution': sentiment_dist,
            'demands': demands,
            'opinion_phase': opinion_phase,
            'solutions': solutions
        })
    
    def _save_results(self):
        """保存分析结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/analysis_result_{timestamp}.json"
        
        # 移除不可序列化的对象
        save_data = {
            k: v for k, v in self.analysis_result.items()
            if k != 'comments' or isinstance(v, (dict, list, str, int, float, bool))
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ 结果已保存: {output_file}")
        
        # 打印核心结果摘要
        print("\n" + "-"*60)
        print("核心分析结果摘要")
        print("-"*60)
        
        print(f"\n【事件类型】{self.analysis_result['topic_analysis'].get('event_type', '未知')}")
        print(f"【核心实体】{self.analysis_result['topic_analysis'].get('core_entity', '未知')}")
        print(f"【舆论阶段】{self.analysis_result['opinion_phase'].get('phase', '未知')}")
        print(f"【判断理由】{self.analysis_result['opinion_phase'].get('reason', '无')}")
        
        print(f"\n【情感分布】")
        for sentiment, count in self.analysis_result['sentiment_distribution'].items():
            print(f"  {sentiment}: {count}")
        
        print(f"\n【主要诉求】")
        for i, demand in enumerate(self.analysis_result['demands'].get('main_demands', [])[:5], 1):
            # print(f"  {i}. {demand.get('demand', '')} (频率:{demand.get('frequency', '未知')})")
            print(f"  {i}. {demand.get('demand', '')} ")
        
        print(f"\n【建议方案】")
        for i, solution in enumerate(self.analysis_result['solutions'].get('suggested_solutions', [])[:5], 1):
            print(f"  {i}. {solution}")
        
        print("-"*60)
    
    def _build_knowledge_graph(self):
        """构建知识图谱"""
        try:
            self.kg_builder.build_complete_graph(self.analysis_result)
        except Exception as e:
            print(f"  ✗ 知识图谱构建失败: {e}")
            print("  提示: 请确保Neo4j数据库已启动并配置正确")
    
    def close(self):
        """关闭资源"""
        self.kg_builder.close()


def main():
    """主函数"""
    import sys
    
    # 检查命令行参数
    json_file = "weibo_comments_full.json"
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    # 创建Pipeline
    pipeline = OpinionAnalysisPipeline(json_file)
    
    try:
        # 运行分析
        result = pipeline.run(
            build_kg=True,      # 是否构建知识图谱
            clear_db=False      # 是否清空数据库
        )
        
        print("\n提示: 你可以使用Neo4j Browser查看知识图谱")
        print("访问: http://localhost:7474")
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n执行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pipeline.close()


if __name__ == "__main__":
    main()

