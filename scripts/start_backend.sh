#!/bin/bash

# AI自动化测试平台 - 后端启动脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_ROOT="$PROJECT_ROOT/backend"
cd "$BACKEND_ROOT"

echo -e "${BLUE}🚀 启动AI自动化测试平台后端服务${NC}"
echo "项目路径: $PROJECT_ROOT"

# 检查Python版本
echo -e "${YELLOW}📋 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python版本: $PYTHON_VERSION${NC}"

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✅ 虚拟环境已激活: $VIRTUAL_ENV${NC}"
else
    echo -e "${YELLOW}⚠️  未检测到虚拟环境，建议使用虚拟环境${NC}"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ 用户取消启动${NC}"
        exit 1
    fi
fi

# 检查环境配置文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在，正在创建...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ 已从 .env.example 创建 .env 文件${NC}"
        echo -e "${YELLOW}📝 请编辑 .env 文件配置数据库等信息${NC}"
    else
        echo -e "${RED}❌ .env.example 文件不存在${NC}"
        exit 1
    fi
fi

# 安装依赖
echo -e "${YELLOW}📦 检查依赖包...${NC}"
if [ -f "requirements.txt" ]; then
    echo "正在安装后端依赖..."
    pip install -r requirements.txt
    echo -e "${GREEN}✅ 后端依赖安装完成${NC}"
else
    echo -e "${RED}❌ 未找到 requirements.txt 文件${NC}"
    exit 1
fi

# 检查数据库连接
echo -e "${YELLOW}🗄️  检查数据库连接...${NC}"
# 这里可以添加数据库连接检查逻辑

# 创建必要的目录
echo -e "${YELLOW}📁 创建必要目录...${NC}"
mkdir -p logs
mkdir -p uploads
mkdir -p data
echo -e "${GREEN}✅ 目录创建完成${NC}"

# 设置环境变量
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 启动服务
echo -e "${BLUE}🌐 启动后端服务...${NC}"
echo "服务地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "按 Ctrl+C 停止服务"
echo ""

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}❌ 端口 8000 已被占用${NC}"
    echo "请检查是否有其他服务在运行，或修改 .env 文件中的 PORT 配置"
    exit 1
fi

# 启动服务
if [ -f "main.py" ]; then
    python3 main.py
elif [ -f "src/auto-test/scenario_ai_api.py" ]; then
    python3 src/auto-test/scenario_ai_api.py
else
    echo -e "${RED}❌ 未找到启动文件${NC}"
    exit 1
fi