#!/usr/bin/env python
"""对比有无哈希索引的等值查询耗时"""
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.query_engine.executor import Executor
from src.query_engine.index import HashIndex
from src.query_engine.parser import parse

def main():
    csv_path = Path(__file__).parent.parent / "data" / "test_data.csv"
    if not csv_path.exists():
        print("Please generate test data first: uv run generate-data")
        return

    # 加载数据
    exec_base = Executor(str(csv_path))
    exec_base._load_data()
    data = exec_base._data

    # 构建索引
    idx = HashIndex("id")
    idx.build(data)
    exec_with_idx = Executor(str(csv_path), index=idx)
    exec_without_idx = Executor(str(csv_path), index=None)

    # 等值查询测试
    test_ids = [12345, 67890, 42, 99999, 1]
    times_with = []
    times_without = []

    for tid in test_ids:
        sql = f"SELECT * FROM data WHERE id = {tid}"
        ast = parse(sql)

        # 无索引
        start = time.perf_counter()
        exec_without_idx.execute(ast)
        elapsed = time.perf_counter() - start
        times_without.append(elapsed)

        # 有索引
        start = time.perf_counter()
        exec_with_idx.execute(ast)
        elapsed = time.perf_counter() - start
        times_with.append(elapsed)

    avg_without = sum(times_without) / len(times_without) * 1000
    avg_with = sum(times_with) / len(times_with) * 1000
    print("=== Hash Index Benchmark ===")
    print(f"Average query time without index: {avg_without:.2f} ms")
    print(f"Average query time with index:    {avg_with:.2f} ms")
    print(f"Speedup: {avg_without/avg_with:.2f}x")

if __name__ == "__main__":
    main()