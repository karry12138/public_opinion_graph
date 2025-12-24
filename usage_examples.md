# 使用示例

## 示例1：完整分析流程

```bash
# 激活虚拟环境（如果还没激活）
venv\Scripts\activate

# 运行完整分析
python main_pipeline.py
```

**输出：**
- 控制台显示分析进度和结果摘要
- 生成 `analysis_result_YYYYMMDD_HHMMSS.json` 文件
- Neo4j中构建知识图谱

## 示例2：生成分析报告

```bash
# 运行可视化工具
python visualizer.py
```

**输出：**
```
============================================================
舆情分析报告
============================================================

【事件概况】
发布方: 上海地铁shmetro
事件类型: 公共交通故障
内容: 【运营信息】目前，5号线因车辆故障...
评论数: 160
回复数: 73
舆论阶段: 发酵期

【情感分布】
  负面: 95 (59.4%)
  中性: 45 (28.1%)
  正面: 20 (12.5%)

【主要诉求】
  1. 致歉信
     频率: 高, 提及用户数: 15
  2. 延误证明
     频率: 高, 提及用户数: 12
  ...
```

## 示例3：单独测试各模块

### 测试数据解析

```bash
python data_parser.py
```

### 测试LLM分析

```bash
python llm_analyzer.py
```

### 测试Neo4j连接

```bash
python kg_builder.py
```

### 测试所有连接

```bash
python test_connection.py
```

## 示例4：Neo4j查询示例

在Neo4j Browser (http://localhost:7474) 中执行：

### 查看整体结构

```cypher
// 查看所有节点和关系
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 100
```

### 查看事件详情

```cypher
// 查看事件及相关信息
MATCH (e:Event)
OPTIONAL MATCH (e)-[:处于]->(p:OpinionPhase)
OPTIONAL MATCH (c:Comment)-[:评论]->(e)
RETURN e, p, count(c) as comment_count
```

### 分析情感分布

```cypher
// 按情感分类统计评论
MATCH (c:Comment)
RETURN c.sentiment as 情感, 
       count(*) as 数量,
       avg(c.intensity) as 平均强度
ORDER BY 数量 DESC
```

### 查找高强度负面评论

```cypher
// 查找强烈负面评论
MATCH (u:User)-[:发表]->(c:Comment)
WHERE c.sentiment = '负面' AND c.intensity >= 8
RETURN u.name as 用户, 
       c.content as 评论内容,
       c.emotion as 情绪,
       c.intensity as 强度
ORDER BY c.intensity DESC
LIMIT 10
```

### 分析用户诉求

```cypher
// 查看诉求及提出者
MATCH (u:User)-[:提出]->(d:Demand)
RETURN d.content as 诉求,
       d.frequency as 频率,
       collect(u.name) as 用户列表,
       count(u) as 用户数
ORDER BY 用户数 DESC
```

### 查看官方回应情况

```cypher
// 查看官方回应
MATCH (o:Organization)-[:发表]->(r:Reply)-[:回复]->(c:Comment)
RETURN o.name as 官方账号,
       c.content as 原评论,
       r.content as 回应内容,
       r.time as 回应时间
ORDER BY r.time
```

### 分析评论网络

```cypher
// 查看谁回复了谁
MATCH (u1:User)-[:发表]->(r:Reply)-[:回复]->(c:Comment)<-[:发表]-(u2:User)
WHERE u1.name <> u2.name
RETURN u1.name as 回复者,
       u2.name as 被回复者,
       count(*) as 互动次数
ORDER BY 互动次数 DESC
LIMIT 20
```

### 查看解决方案

```cypher
// 查看所有解决方案
MATCH (s:Solution)
OPTIONAL MATCH (o:Organization)-[:采取]->(s)
RETURN s.type as 类型,
       s.content as 内容,
       o.name as 实施方
ORDER BY s.type
```

## 示例5：Python脚本调用

### 作为模块使用

```python
from data_parser import WeiboDataParser
from llm_analyzer import LLMAnalyzer
from kg_builder import KnowledgeGraphBuilder

# 1. 解析数据
parser = WeiboDataParser("weibo_comments_full.json")
event_info = parser.extract_event_info()
comments = parser.extract_comments(limit=10)

# 2. LLM分析
analyzer = LLMAnalyzer()
topic_analysis = analyzer.analyze_topic(
    event_info['topic_content'],
    event_info['author']
)

# 3. 构建知识图谱
kg = KnowledgeGraphBuilder()
event_id = kg.create_event_node(event_info, topic_analysis)
kg.close()
```

### 自定义Pipeline

```python
from main_pipeline import OpinionAnalysisPipeline

# 创建pipeline
pipeline = OpinionAnalysisPipeline("your_data.json")

# 只运行分析，不构建图谱
result = pipeline.run(build_kg=False)

# 访问结果
print(result['opinion_phase'])
print(result['sentiment_distribution'])
print(result['demands'])

pipeline.close()
```

## 示例6：批量处理多个文件

创建脚本 `batch_process.py`：

```python
import os
import glob
from main_pipeline import OpinionAnalysisPipeline

# 获取所有JSON文件
json_files = glob.glob("data/*.json")

for json_file in json_files:
    print(f"\n处理文件: {json_file}")
    
    pipeline = OpinionAnalysisPipeline(json_file)
    
    try:
        result = pipeline.run(build_kg=True, clear_db=False)
        print(f"✓ {json_file} 处理完成")
    except Exception as e:
        print(f"✗ {json_file} 处理失败: {e}")
    finally:
        pipeline.close()
```

## 示例7：导出和分享结果

### 导出图谱数据

```python
from visualizer import GraphVisualizer

visualizer = GraphVisualizer()

# 生成报告
report = visualizer.generate_report()
with open('report.txt', 'w', encoding='utf-8') as f:
    f.write(report)

# 导出JSON数据
visualizer.export_graph_data('graph_data.json')

visualizer.close()
```

### 导出Neo4j数据

在Neo4j Browser中执行：

```cypher
// 导出为JSON格式（需要APOC插件）
CALL apoc.export.json.all("opinion_graph.json", {useTypes:true})
```

## 常用命令速查

```bash
# 环境管理
venv\Scripts\activate              # 激活虚拟环境
pip install -r requirements.txt    # 安装依赖
pip freeze > requirements.txt      # 更新依赖列表

# 测试
python test_connection.py          # 测试所有连接
python data_parser.py              # 测试数据解析
python llm_analyzer.py             # 测试LLM
python kg_builder.py               # 测试Neo4j

# 运行
python main_pipeline.py            # 完整分析
python visualizer.py               # 生成报告

# Neo4j管理
neo4j console                      # 启动Neo4j
neo4j stop                         # 停止Neo4j
neo4j status                       # 查看状态
```

## 故障排查

### 问题：LLM调用超时

**解决方案：**
```python
# 在 llm_analyzer.py 中增加超时设置
response = self.client.chat.completions.create(
    model=self.model,
    messages=[...],
    timeout=60  # 增加超时时间
)
```

### 问题：Neo4j内存不足

**解决方案：**
修改Neo4j配置文件 `neo4j.conf`：
```
dbms.memory.heap.initial_size=1g
dbms.memory.heap.max_size=2g
```

### 问题：处理大量数据

**解决方案：**
```python
# 分批处理评论
comments = parser.extract_comments()
batch_size = 20

for i in range(0, len(comments), batch_size):
    batch = comments[i:i+batch_size]
    # 处理batch
```

