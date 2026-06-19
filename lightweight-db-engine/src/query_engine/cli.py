#!/usr/bin/env python
"""命令行交互界面"""
import sys
import time
from pathlib import Path
from .parser import parse
from .executor import Executor
from .index import HashIndex

def main():
    csv_path = Path(__file__).parent.parent.parent / "data" / "test_data.csv"
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}. Run 'uv run generate-data' first.")
        sys.exit(1)

    # 可选：构建索引（默认对 id 列）
    print("Loading data and building index on 'id' column...")
    exec_no_index = Executor(str(csv_path), index=None)
    exec_no_index._load_data()  # 加载数据
    data = exec_no_index._data
    index = HashIndex("id")
    index.build(data)
    exec_with_index = Executor(str(csv_path), index=index)

    print("\n=== Lightweight DB Engine CLI ===")
    print("Supported SQL: SELECT ... FROM data WHERE ... ORDER BY ...")
    print("Example: SELECT name, age FROM data WHERE age > 30 ORDER BY age DESC")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            sql = input("db> ").strip()
            if sql.lower() == "exit":
                break
            if not sql:
                continue
            # 简单解析
            try:
                ast = parse(sql)
                # 判断是否使用索引（等值查询 id）
                use_index = False
                if ast.where and "id =" in ast.where:
                    use_index = True
                executor = exec_with_index if use_index else exec_no_index
                start = time.perf_counter()
                result = executor.execute(ast)
                elapsed = time.perf_counter() - start
                # 输出结果
                if result:
                    # 打印表头
                    if len(result) > 0:
                        headers = result[0].keys()
                        print(" | ".join(headers))
                        print("-" * 50)
                        for row in result[:20]:  # 最多显示20行
                            print(" | ".join(str(row.get(h, "")) for h in headers))
                        if len(result) > 20:
                            print(f"... and {len(result)-20} more rows")
                else:
                    print("No results.")
                print(f"Time: {elapsed*1000:.2f} ms")
            except Exception as e:
                print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nBye")
            break

if __name__ == "__main__":
    main()