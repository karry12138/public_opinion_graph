"""
测试连接脚本 - 检查所有依赖是否配置正确
"""
import sys


def test_imports():
    """测试依赖包导入"""
    print("测试Python依赖包...")
    
    try:
        import openai
        print("  ✓ openai")
    except ImportError:
        print("  ✗ openai - 请运行: pip install openai")
        return False
    
    try:
        import neo4j
        print("  ✓ neo4j")
    except ImportError:
        print("  ✗ neo4j - 请运行: pip install neo4j")
        return False
    
    try:
        import dotenv
        print("  ✓ python-dotenv")
    except ImportError:
        print("  ✗ python-dotenv - 请运行: pip install python-dotenv")
        return False
    
    try:
        import pandas
        print("  ✓ pandas")
    except ImportError:
        print("  ✗ pandas - 请运行: pip install pandas")
        return False
    
    return True


def test_config():
    """测试配置文件"""
    print("\n测试配置文件...")
    
    try:
        import config
        print("  ✓ config.py 已加载")
        
        if not config.DASHSCOPE_API_KEY:
            print("  ⚠ 警告: DASHSCOPE_API_KEY 未配置")
            print("    请在 .env 文件中配置 API Key")
            return False
        else:
            print(f"  ✓ API Key: {config.DASHSCOPE_API_KEY[:10]}...")
        
        if config.NEO4J_PASSWORD == "password":
            print("  ⚠ 警告: NEO4J_PASSWORD 使用默认值")
            print("    建议修改为实际的Neo4j密码")
        else:
            print("  ✓ Neo4j密码已配置")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 配置文件错误: {e}")
        return False


def test_neo4j():
    """测试Neo4j连接"""
    print("\n测试Neo4j连接...")
    
    try:
        from neo4j import GraphDatabase
        import config
        
        driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record['test'] == 1:
                print("  ✓ Neo4j连接成功")
                
                # 检查是否有数据
                result = session.run("MATCH (n) RETURN count(n) as count")
                count = result.single()['count']
                print(f"  ✓ 数据库中有 {count} 个节点")
                
                driver.close()
                return True
        
    except Exception as e:
        print(f"  ✗ Neo4j连接失败: {e}")
        print("\n  可能的原因:")
        print("  1. Neo4j未启动 - 请启动Neo4j服务")
        print("  2. 用户名或密码错误 - 检查 .env 配置")
        print("  3. 端口被占用 - 检查7687端口")
        print("  4. 防火墙阻止 - 检查防火墙设置")
        return False


def test_llm_api():
    """测试LLM API连接"""
    print("\n测试通义千问API连接...")
    
    try:
        from openai import OpenAI
        import config
        
        client = OpenAI(
            api_key=config.DASHSCOPE_API_KEY,
            base_url=config.DASHSCOPE_BASE_URL
        )
        
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[
                {"role": "user", "content": "你好，这是一个测试。请回复'测试成功'"}
            ],
            max_tokens=10
        )
        
        reply = response.choices[0].message.content
        print(f"  ✓ API连接成功")
        print(f"  ✓ 模型响应: {reply}")
        return True
        
    except Exception as e:
        print(f"  ✗ API连接失败: {e}")
        print("\n  可能的原因:")
        print("  1. API Key错误 - 检查 .env 中的 DASHSCOPE_API_KEY")
        print("  2. 网络问题 - 检查网络连接")
        print("  3. API余额不足 - 检查账户余额")
        print("  4. 模型名称错误 - 确认 MODEL_NAME 配置")
        return False


def test_data_file():
    """测试数据文件"""
    print("\n测试数据文件...")
    
    try:
        import json
        import os
        
        data_file = "weibo_comments_full.json"
        
        if not os.path.exists(data_file):
            print(f"  ✗ 数据文件不存在: {data_file}")
            return False
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"  ✓ 数据文件加载成功")
        print(f"  ✓ 评论组数量: {data.get('comment_groups_count', 0)}")
        print(f"  ✓ 总回复数: {data.get('total_replies', 0)}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 数据文件错误: {e}")
        return False


def main():
    """主测试流程"""
    print("="*70)
    print("舆情分析系统 - 环境测试")
    print("="*70)
    
    results = {
        '依赖包': test_imports(),
        '配置文件': test_config(),
        '数据文件': test_data_file(),
        'Neo4j数据库': test_neo4j(),
        'LLM API': test_llm_api()
    }
    
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)
    
    all_passed = True
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n✓ 所有测试通过！可以运行 main_pipeline.py")
        return 0
    else:
        print("\n⚠ 部分测试失败，请根据提示修复问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())

