# 微博舆情分析知识图谱系统

这是一个基于大模型和知识图谱的微博舆情分析系统，能够自动分析微博帖子的评论数据，提取关键信息，判断舆论发展阶段，并构建知识图谱。

## 功能特性

- 📊 **数据解析**: 解析微博JSON格式数据
- 🤖 **智能分析**: 使用通义千问API进行：
  - 主题提取
  - 情感分析
  - 诉求提取
  - 舆论周期判断
  - 解决方案建议
- 🕸️ **知识图谱**: 构建Neo4j知识图谱，包含：
  - 事件、用户、评论、回复节点
  - 情感、诉求、解决方案节点
  - 多种关系类型

## 系统架构

```
数据输入 → 数据解析 → LLM分析 → 知识图谱构建 → 结果输出
  ↓          ↓          ↓           ↓            ↓
JSON    event_info   sentiment   Neo4j      analysis.json
        comments     phase       nodes      + 图谱可视化
        stats        demands     relations
```

## 前置要求

1. **Python 3.8+**
2. **Neo4j 数据库**
   - 安装教程：https://blog.csdn.net/weixin_66401877/article/details/153195602
   - 下载安装：https://neo4j.com/download/
   - 启动服务：默认端口 7687
3. **通义千问 API**
   - 获取API Key：https://dashscope.aliyun.com/

## 安装步骤

### 1. 克隆或下载项目

```bash
cd public_opinion_graph
```

### 2. 创建虚拟环境（推荐）

```bash
# 快速环境配置与环境测试脚本（Windows推荐）
quick_start.bat
```

```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填入配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 通义千问 API 配置
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Neo4j 数据库配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# 模型配置
MODEL_NAME=qwen-plus
```

### 5. 启动Neo4j数据库

```bash
# 启动Neo4j
neo4j console

# 或使用Docker
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/your_password neo4j:latest
```

访问 http://localhost:7474 确认Neo4j已启动。

## 使用方法

### 快速开始

```bash
python main_pipeline.py
```

### 测试各个模块

```bash
# 测试数据解析
python data_parser.py

# 测试LLM分析
python llm_analyzer.py

# 测试知识图谱构建
python kg_builder.py
```

### 指定输入文件

```bash
python main_pipeline.py your_weibo_data.json
```

## 输出结果

### 1. 分析结果JSON

系统会生成 `analysis_result_YYYYMMDD_HHMMSS.json` 文件，包含：

```json
{
  "event_info": {...},
  "topic_analysis": {...},
  "sentiment_distribution": {...},
  "opinion_phase": {...},
  "demands": {...},
  "solutions": {...}
}
```

### 2. Neo4j知识图谱

在Neo4j Browser中执行查询：

```cypher
// 查看所有节点
MATCH (n) RETURN n LIMIT 100

// 查看事件及其关系
MATCH (e:Event)-[r]->(n) RETURN e, r, n

// 查看负面评论
MATCH (c:Comment {sentiment: "负面"}) RETURN c

// 查看用户诉求
MATCH (u:User)-[:提出]->(d:Demand) RETURN u, d

// 查看舆论阶段
MATCH (e:Event)-[:处于]->(p:OpinionPhase) RETURN e, p
```

### 3. 控制台输出

运行时会打印：
- 数据统计信息
- 分析进度
- 核心结果摘要
- 图谱构建状态

## 知识图谱结构

### 节点类型

- **Event**: 事件节点
- **Organization**: 组织机构（官方账号）
- **User**: 用户节点
- **Comment**: 主评论节点
- **Reply**: 回复节点
- **OpinionPhase**: 舆论周期节点
- **Demand**: 诉求节点
- **Solution**: 解决方案节点

### 关系类型

- `发布`: Organization → Event
- `处于`: Event → OpinionPhase
- `发表`: User → Comment/Reply
- `评论`: Comment → Event
- `回复`: Reply → Comment
- `提出`: User → Demand
- `包含`: Comment → Demand
- `采取`: Organization → Solution
- `针对`: Solution → Event

## 配置说明

### 通义千问模型选择

在 `.env` 中可配置不同模型：

- `qwen-plus`: 平衡性能和成本（推荐）
- `qwen-max`: 最强性能
- `qwen-turbo`: 快速响应

### 调整分析数量

在 `main_pipeline.py` 中修改：

```python
# 限制评论分析数量
comments = self.parser.extract_comments()[:20]  # 修改这里

# 限制情感分析数量
def analyze_sentiment_batch(self, comments: List[Dict]) -> List[Dict]:
    for comment in comments[:20]:  # 修改这里
```

## 常见问题

### 1. Neo4j连接失败

```
确保Neo4j已启动：neo4j status
检查端口是否正确：默认7687
验证用户名密码
```

### 2. API调用失败

```
检查API Key是否正确
确认网络连接
查看API余额
```

### 3. 中文分词问题

```
确保安装了jieba：pip install jieba
```

### 4. 内存不足

```
减少批量处理数量
分批次处理数据
```

## 项目结构

```
public_opinion_graph/
├── config.py              # 配置管理
├── data_parser.py         # 数据解析模块
├── llm_analyzer.py        # LLM分析模块
├── kg_builder.py          # 知识图谱构建
├── main_pipeline.py       # 主流程
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
├── README.md             # 使用文档
├── weibo_comments_full.json  # 示例数据
└── analysis_result_*.json    # 分析结果
```

## 扩展开发

### 添加新的分析维度

在 `llm_analyzer.py` 中添加新方法：

```python
def analyze_new_dimension(self, data):
    prompt = "你的分析提示词..."
    result = self._call_llm(prompt)
    return result
```

### 自定义节点类型

在 `kg_builder.py` 中添加：

```python
def create_custom_node(self, data: Dict) -> str:
    with self.driver.session() as session:
        query = """
        CREATE (n:CustomNode {property: $value})
        RETURN elementId(n) as id
        """
        result = session.run(query, value=data['value'])
        return result.single()['id']
```

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提Issue。

