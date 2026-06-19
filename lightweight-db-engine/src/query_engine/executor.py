import csv
from typing import List, Dict, Any, Optional
import operator
from .parser import QueryAST
from .index import HashIndex

class Executor:
    def __init__(self, csv_path: str, index: Optional[HashIndex] = None):
        self.csv_path = csv_path
        self.index = index
        self._data: List[Dict] = None  # 懒加载

    def _load_data(self):
        if self._data is None:
            self._data = []
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 转换数字类型
                    for k, v in row.items():
                        if v.isdigit():
                            row[k] = int(v)
                        else:
                            try:
                                row[k] = float(v)
                            except ValueError:
                                pass
                    self._data.append(row)

    def execute(self, ast: QueryAST) -> List[Dict]:
        self._load_data()
        # 过滤
        filtered = self._filter(self._data, ast.where)
        # 聚合 vs 普通查询
        if ast.aggregates:
            # 聚合查询（无 GROUP BY，全表聚合）
            result = self._aggregate(filtered, ast.aggregates, ast.select_cols)
            return [result] if result else []
        else:
            # 普通查询：投影 + 排序
            projected = self._project(filtered, ast.select_cols)
            if ast.order_by:
                projected = self._sort(projected, ast.order_by[0], ast.order_by[1])
            return projected

    def _filter(self, data: List[Dict], where_cond: Optional[str]) -> List[Dict]:
        if not where_cond:
            return data
        # 使用索引优化等值查询
        if self.index and self._is_eq_index_condition(where_cond):
            # 尝试从索引获取行
            col, val = self._parse_eq_condition(where_cond)
            if col in self.index.index_map:
                rows = self.index.get_rows(val, self._data)
                return rows
        # 否则全表扫描 + 动态条件评估
        result = []
        for row in data:
            if self._eval_condition(row, where_cond):
                result.append(row)
        return result

    def _is_eq_index_condition(self, cond: str) -> bool:
        # 简单判断：包含 = 且没有其他运算符
        return "=" in cond and not any(op in cond for op in [">", "<", ">=", "<=", "!="])

    def _parse_eq_condition(self, cond: str) -> tuple:
        # 解析 "col = value"
        parts = cond.split("=")
        col = parts[0].strip()
        val = parts[1].strip().strip("'")
        # 尝试数字转换
        try:
            val = int(val)
        except:
            try:
                val = float(val)
            except:
                pass
        return col, val

    def _eval_condition(self, row: Dict, cond: str) -> bool:
        # 安全评估：替换变量名为实际值
        # 注意：eval 有安全风险，但输入可控（仅用于实验）
        local_dict = {}
        for k, v in row.items():
            local_dict[k] = v
        try:
            # 替换 AND/OR 为 python 逻辑运算符
            expr = cond.replace("AND", "and").replace("OR", "or")
            # 处理不等号
            expr = expr.replace("!=", "!=")
            return eval(expr, {"__builtins__": {}}, local_dict)
        except:
            return False

    def _project(self, data: List[Dict], cols: List[str]) -> List[Dict]:
        if not cols:  # SELECT *
            return data
        result = []
        for row in data:
            new_row = {col: row[col] for col in cols if col in row}
            result.append(new_row)
        return result

    def _sort(self, data: List[Dict], col: str, direction: str) -> List[Dict]:
        reverse = (direction.upper() == "DESC")
        return sorted(data, key=lambda x: x.get(col, 0), reverse=reverse)

    def _aggregate(self, data: List[Dict], aggregates: Dict[str, str], select_cols: List[str]) -> Dict:
        result = {}
        # 处理聚合函数
        for col, func in aggregates.items():
            values = [row[col] for row in data if col in row]
            if not values:
                result[f"{func}({col})"] = None
                continue
            if func == "COUNT":
                result[f"{func}({col})"] = len(values)
            elif func == "SUM":
                result[f"{func}({col})"] = sum(values)
            elif func == "AVG":
                result[f"{func}({col})"] = sum(values) / len(values)
            elif func == "MAX":
                result[f"{func}({col})"] = max(values)
            elif func == "MIN":
                result[f"{func}({col})"] = min(values)
        # 如果 SELECT 中还有普通列，忽略（因为没有 GROUP BY）
        return result