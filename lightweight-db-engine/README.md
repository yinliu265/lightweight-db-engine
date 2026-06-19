# Lightweight DB Engine

轻量级数据库引擎，支持：
- 单表查询（条件过滤、聚合、排序、投影）
- 哈希索引（性能对比实验）
- 列式存储（与行式对比实验）
- 自然语言转 SQL（调用 Groq API）

## 快速开始

```bash
# 安装 uv（如果没有）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆仓库
git clone https://github.com/yourusername/lightweight-db-engine.git
cd lightweight-db-engine

# 安装依赖
uv sync

# 生成测试数据（10万行）
uv run generate-data

# 启动命令行查询界面
uv run db-cli

# 运行实验
uv run hash-bench
uv run col-bench

# 测试自然语言接口
uv run nl-test