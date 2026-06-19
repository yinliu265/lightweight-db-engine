import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.query_engine.parser import parse
from src.query_engine.executor import Executor

class TestQueryEngine(unittest.TestCase):
    def setUp(self):
        # 创建临时 CSV
        self.csv_path = Path(__file__).parent / "test_small.csv"
        with open(self.csv_path, 'w') as f:
            f.write("id,name,age\n1,Alice,30\n2,Bob,25\n3,Charlie,35")
        self.executor = Executor(str(self.csv_path))

    def tearDown(self):
        self.csv_path.unlink()

    def test_select_all(self):
        ast = parse("SELECT * FROM data")
        result = self.executor.execute(ast)
        self.assertEqual(len(result), 3)

    def test_where(self):
        ast = parse("SELECT name FROM data WHERE age > 30")
        result = self.executor.execute(ast)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Charlie')

if __name__ == "__main__":
    unittest.main()