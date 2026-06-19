#!/usr/bin/env python
"""生成 CSV 测试数据，至少 10 万行"""
import csv
import random
from pathlib import Path
from faker import Faker

def main():
    fake = Faker()
    rows = 100_000  # 10万行
    output_file = Path(__file__).parent / "test_data.csv"
    print(f"Generating {rows} rows...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'age', 'salary', 'city', 'score'])
        for i in range(rows):
            writer.writerow([
                i,
                fake.name(),
                random.randint(18, 70),
                random.randint(30000, 150000),
                fake.city(),
                round(random.uniform(0, 100), 2)
            ])
    print(f"Generated {output_file} with {rows} rows")

if __name__ == "__main__":
    main()