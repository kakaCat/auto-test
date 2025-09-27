#!/bin/bash

# AI编排模块部署脚本
# Deploy AI Orchestration Module

set -e  # 遇到错误立即退出

echo "🚀 开始部署AI编排模块..."

# 检查当前目录
if [ ! -f "backend/start_api_v2.py" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 1. 环境检查
echo "1️⃣ 检查环境..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python版本: $python_version"

# 检查Node.js版本
node_version=$(node --version 2>&1)
echo "Node.js版本: $node_version"

# 2. 安装后端依赖
echo "2️⃣ 安装后端依赖..."
cd backend

# 安装基础依赖
echo "安装基础依赖..."
pip install -r requirements.txt

# 安装AI编排依赖
echo "安装AI编排依赖..."
pip install -r requirements-ai.txt

echo "✅ 后端依赖安装完成"

# 3. 初始化数据库
echo "3️⃣ 初始化数据库..."

# 检查数据库文件是否存在
if [ ! -f "auto_test.db" ]; then
    echo "创建新数据库..."
    touch auto_test.db
fi

# 执行AI编排表创建
echo "创建AI编排相关表..."
sqlite3 auto_test.db < scripts/database/create_ai_orchestration_tables.sql

echo "✅ 数据库初始化完成"

# 4. 配置环境变量
echo "4️⃣ 配置环境变量..."

# 创建.env文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "创建.env配置文件..."
    cat > .env << EOF
# AI编排模块配置
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DEFAULT_LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.1

# MCP配置
MCP_TOOLS_ENABLED=true
MAX_CONCURRENT_EXECUTIONS=5
EXECUTION_TIMEOUT=300

# 服务配置
HOST=0.0.0.0
PORT=8002
DEBUG=false
LOG_LEVEL=INFO

# 数据库配置
DATABASE_PATH=auto_test.db
EOF
    echo "✅ .env文件已创建，请根据需要修改配置"
else
    echo "✅ .env文件已存在"
fi

# 5. 安装前端依赖
echo "5️⃣ 安装前端依赖..."
cd ../frontend

# 检查package.json是否存在
if [ -f "package.json" ]; then
    echo "安装前端依赖..."
    npm install
    echo "✅ 前端依赖安装完成"
else
    echo "⚠️  前端package.json不存在，跳过前端依赖安装"
fi

# 6. 运行测试
echo "6️⃣ 运行功能测试..."
cd ../backend

# 运行基础测试
echo "运行基础功能测试..."
python test_orchestration.py

# 7. 启动服务（可选）
echo "7️⃣ 准备启动服务..."

cat << EOF

🎉 AI编排模块部署完成！

📋 部署清单:
  ✅ 环境检查完成
  ✅ 后端依赖安装完成
  ✅ 数据库初始化完成
  ✅ 环境配置完成
  ✅ 前端依赖安装完成
  ✅ 功能测试通过

🚀 启动服务:

1. 启动后端服务:
   cd backend
   python start_api_v2.py

2. 启动前端服务:
   cd frontend
   npm run dev

🌐 访问地址:
  - 前端界面: http://localhost:5173
  - AI编排页面: http://localhost:5173/#/ai-orchestration
  - API文档: http://127.0.0.1:8002/docs

📖 文档:
  - 实现报告: docs/ai-platform/API_ORCHESTRATION_IMPLEMENTATION_REPORT.md
  - 设计文档: docs/ai-platform/03_PHASE1_API_ORCHESTRATION_DESIGN.md
  - 实施指南: docs/ai-platform/04_PHASE1_IMPLEMENTATION_GUIDE.md

🔧 配置说明:
  - 如需使用真实LLM，请在 backend/.env 中配置 OPENAI_API_KEY
  - 未配置时会自动使用模拟LLM进行测试
  - 所有配置项都有合理的默认值

EOF

echo "✨ 部署完成！AI编排模块已准备就绪"