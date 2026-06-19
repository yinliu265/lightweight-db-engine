#!/usr/bin/env python
"""对比行式(CSV)与列式存储的性能"""
import time
import tempfile
import shutil
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.query_engine.executor import Executor
from src.columnar_storage.columnar_writer import write_columnar
from src.columnar_storage.columnar_reader import read_columnar

def main():
    csv_path = Path(__file__).parent.parent.parent / "data" / "test_data.csv"
    if not csv_path.exists():
        print("Please generate test data first: uv run generate-data")
        return

    # 加载 CSV 数据（行式）
    exec_csv = Executor(str(csv_path))
    exec_csv._load_data()
    data = exec_csv._data

    # 准备列式存储
    temp_dir = tempfile.mkdtemp()
    columns = list(data[0].keys())
    write_columnar(data, columns, temp_dir)

    # 实验1：聚合查询 (SUM salary, AVG score)
    print("=== Aggregate Query: SUM(salary), AVG(score) ===")
    # 行式
    start = time.perf_counter()
    # 手动计算聚合
    sum_sal = sum(row["salary"] for row in data)
    avg_score = sum(row["score"] for row in data) / len(data)
    row_time = time.perf_counter() - start
    print(f"Row-store time: {row_time*1000:.2f} ms")

    # 列式：只读 salary 和 score 两列
    start = time.perf_counter()
    col_data = read_columnar(["salary", "score"], temp_dir)
    sum_sal_col = sum(row["salary"] for row in col_data)
    avg_score_col = sum(row["score"] for row in col_data) / len(col_data)
    col_time = time.perf_counter() - start
    print(f"Column-store time: {col_time*1000:.2f} ms")
    print(f"Speedup: {row_time/col_time:.2f}x\n")

    # 实验2：全行读取 (SELECT *)
    print("=== Full Row Read: SELECT * ===")
    # 行式
    start = time.perf_counter()
    all_rows_csv = list(data)  # 已经加载
    row_full_time = time.perf_counter() - start
    print(f"Row-store time: {row_full_time*1000:.2f} ms")

    # 列式：读取所有列
    start = time.perf_counter()
    all_rows_col = read_columnar(columns, temp_dir)
    col_full_time = time.perf_counter() - start
    print(f"Column-store time: {col_full_time*1000:.2f} ms")
    print(f"Row-store is {col_full_time/row_full_time:.2f}x faster for full read\n")

    # 清理
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()