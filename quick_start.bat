@echo off
chcp 65001 > nul
echo ========================================
echo 舆情分析系统 - 快速启动脚本
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\" (
    echo [1/5] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 虚拟环境创建失败
        pause
        exit /b 1
    )
) else (
    echo [1/5] 虚拟环境已存在
)

echo [2/5] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 虚拟环境激活失败
    pause
    exit /b 1
)

echo [3/5] 安装依赖包...
echo 正在升级pip...
python -m pip install --upgrade pip -q
echo 正在安装依赖（这可能需要几分钟）...
pip install -r requirements.txt --no-cache-dir
if errorlevel 1 (
    echo.
    echo 错误: 依赖安装失败
    echo.
    echo 尝试使用备选方案（逐个安装）...
    pip install openai neo4j python-dotenv pandas numpy jieba requests tqdm matplotlib pyvis
    if errorlevel 1 (
        echo 依赖安装仍然失败，请手动运行：
        echo   pip install openai neo4j python-dotenv pandas
        pause
        exit /b 1
    )
)

REM 检查.env文件
if not exist ".env" (
    echo.
    echo [4/5] 警告: .env 文件不存在
    echo 正在从模板创建 .env 文件...
    copy .env_template .env > nul
    echo.
    echo 重要: 请编辑 .env 文件，填入你的配置:
    echo   - DASHSCOPE_API_KEY: 通义千问API密钥
    echo   - NEO4J_PASSWORD: Neo4j数据库密码
    echo.
    notepad .env
    echo 配置完成后，按任意键继续...
    pause > nul
) else (
    echo [4/5] .env 文件已存在
)

echo [5/5] 测试环境配置...
python test_connection.py
if errorlevel 1 (
    echo.
    echo 环境测试未完全通过，请检查上述错误
    echo 按任意键退出...
    pause > nul
    exit /b 1
)

echo.
echo ========================================
echo 环境配置完成！
echo ========================================
echo.
echo 现在可以运行以下命令:
echo   python main_pipeline.py     - 运行完整分析流程
echo   python visualizer.py        - 生成分析报告
echo   python data_parser.py       - 测试数据解析
echo.
pause

