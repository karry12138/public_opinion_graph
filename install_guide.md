# 安装和配置指南

## 快速开始步骤

### 1. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（复制 .env_template）：

```bash
copy .env_template .env
```

编辑 `.env` 文件，填入你的配置：

```env
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx  # 你的通义千问API Key
NEO4J_PASSWORD=your_neo4j_password  # 你的Neo4j密码
```

### 3. 启动Neo4j数据库

**方式1：使用Neo4j Desktop**
1. 下载：https://neo4j.com/download/
2. 创建新数据库
3. 设置密码并启动

**方式2：使用Docker（推荐）**
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest
```

访问 http://localhost:7474 验证Neo4j是否启动成功。

### 4. 获取通义千问API Key

1. 访问：https://dashscope.aliyun.com/
2. 登录/注册阿里云账号
3. 开通DashScope服务
4. 创建API Key
5. 复制API Key到 `.env` 文件

### 5. 运行系统

```bash
python main_pipeline.py
```

## 测试各模块

```bash
# 测试数据解析
python data_parser.py

# 测试LLM分析（需要API Key）
python llm_analyzer.py

# 测试Neo4j连接（需要Neo4j运行）
python kg_builder.py
```

## 常见问题

### 问题1：找不到模块

```bash
# 确保虚拟环境已激活
# Windows:
venv\Scripts\activate

# 重新安装依赖
pip install -r requirements.txt
```

### 问题2：Neo4j连接失败

```
错误: ServiceUnavailable: Failed to establish connection
解决: 
1. 确认Neo4j已启动
2. 检查端口7687是否被占用
3. 验证用户名密码是否正确
```

### 问题3：API调用失败

```
错误: AuthenticationError
解决:
1. 检查DASHSCOPE_API_KEY是否正确
2. 确认API余额是否充足
3. 验证网络连接
```

## 目录结构说明

```
project/
├── .env                    # 环境变量配置（需要创建）
├── .env_template          # 环境变量模板
├── requirements.txt       # Python依赖
├── config.py             # 配置管理
├── data_parser.py        # 数据解析
├── llm_analyzer.py       # LLM分析
├── kg_builder.py         # 知识图谱构建
├── main_pipeline.py      # 主程序
├── README.md             # 项目说明
└── weibo_comments_full.json  # 示例数据
```

