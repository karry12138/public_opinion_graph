"""
配置文件
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 通义千问 API 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen-plus")

# Neo4j 配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# 舆论周期定义
OPINION_PHASES = ["潜伏期", "爆发期", "发酵期", "消退期", "平息期"]

# 情感分类
SENTIMENT_TYPES = ["正面", "负面", "中性"]

# 检查必要配置
def check_config():
    """检查配置是否完整"""
    if not DASHSCOPE_API_KEY:
        raise ValueError("请在 .env 文件中配置 DASHSCOPE_API_KEY")
    if not NEO4J_PASSWORD or NEO4J_PASSWORD == "password":
        print("警告: 请在 .env 文件中配置正确的 NEO4J_PASSWORD")
    return True

