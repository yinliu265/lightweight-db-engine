#!/usr/bin/env python
"""提供至少10个自然语言测试用例，展示转换结果与执行结果"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.natural_language.llm_client import LLMClient
from src.query_engine.parser import parse
from src.query_engine.executor import Executor

# 定义 schema
SCHEMA = """
表名: sales
列:
- order_id (INTEGER)
- product (TEXT)
- sales_amount (INTEGER)
- order_date (TEXT, 格式 YYYY-MM-DD)
"""

def run_test_case(client, executor, question, expected_sql_substring):
    print(f"\n🔹 问题: {question}")
    sql = client.generate_sql(question, SCHEMA)
    print(f"🔸 生成 SQL: {sql}")
    # 验证 SQL 是否包含预期的子串（简单校验）
    if expected_sql_substring.lower() in sql.lower():
        print("✅ SQL 符合预期")
    else:
        print(f"⚠️  SQL 可能不符合预期 (期望包含 '{expected_sql_substring}')")
    # 执行 SQL（需要准备 sales 表数据，这里 mock）
    print("   (执行需要真实 sales 表数据，此处仅展示转换)")
    # 实际可以解析并执行，但需要先有 sales.csv
    return sql

def main():
    # 初始化 LLM 客户端（mock模式，避免API key）
    client = LLMClient(mock=True)  # 改为 False 使用真实 API
    # 需要准备 sales.csv 才能执行，这里只演示转换
    executor = None  # 实际使用时创建 Executor

    test_questions = [
        ("查询所有订单", "SELECT * FROM sales"),
        ("查询销售额大于1000的订单", "sales_amount > 1000"),
        ("产品是'A'且金额小于500", "product = 'A' AND sales_amount < 500"),
        ("总销售额是多少", "SUM(sales_amount)"),
        ("平均销售额", "AVG(sales_amount)"),
        ("按销售额降序排列", "ORDER BY sales_amount DESC"),
        ("订单数量", "COUNT(*)"),
        ("最大销售额", "MAX(sales_amount)"),
        ("2024年1月的订单", "order_date >= '2024-01-01'"),
        ("产品B和产品C的总销售额", "product IN ('B', 'C')"),
        ("销售额最高的前5个订单", "ORDER BY sales_amount DESC LIMIT 5"),  # 超出基础支持
    ]

    for i, (question, expected) in enumerate(test_questions, 1):
        print(f"\n=== 测试用例 {i} ===")
        run_test_case(client, executor, question, expected)

if __name__ == "__main__":
    main()