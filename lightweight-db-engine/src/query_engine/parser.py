from typing import List, Dict, Any, Optional, Tuple
from .tokenizer import tokenize

class QueryAST:
    def __init__(self):
        self.select_cols: List[str] = []      # 投影列，空列表表示 *
        self.aggregates: Dict[str, str] = {}  # {"col": "SUM"} 等
        self.table: str = ""
        self.where: Optional[Dict] = None     # 条件树
        self.order_by: Optional[Tuple[str, str]] = None  # (col, 'ASC'/'DESC')
        self.is_count_star: bool = False

def parse(sql: str) -> QueryAST:
    tokens = tokenize(sql)
    # 简化解析：只支持基本语法，使用状态机
    ast = QueryAST()
    i = 0
    # 期待 SELECT
    if i >= len(tokens) or tokens[i][1].upper() != "SELECT":
        raise SyntaxError("Missing SELECT")
    i += 1
    # 解析选择列
    if tokens[i][1] == "*":
        ast.select_cols = []
        i += 1
    else:
        while i < len(tokens) and tokens[i][0] != "KEYWORD" or tokens[i][1].upper() != "FROM":
            if tokens[i][0] == "IDENT":
                col = tokens[i][1]
                # 检查前面是否有聚合函数
                if i > 0 and tokens[i-1][0] == "KEYWORD" and tokens[i-1][1].upper() in ("COUNT","SUM","AVG","MAX","MIN"):
                    agg = tokens[i-1][1].upper()
                    ast.aggregates[col] = agg
                else:
                    ast.select_cols.append(col)
            i += 1
            if i < len(tokens) and tokens[i][0] == "PUNCT" and tokens[i][1] == ",":
                i += 1
    # 期待 FROM
    if i >= len(tokens) or tokens[i][1].upper() != "FROM":
        raise SyntaxError("Missing FROM")
    i += 1
    if i >= len(tokens) or tokens[i][0] != "IDENT":
        raise SyntaxError("Missing table name")
    ast.table = tokens[i][1]
    i += 1
    # 可选 WHERE
    if i < len(tokens) and tokens[i][1].upper() == "WHERE":
        i += 1
        ast.where = parse_where(tokens, i)
        # 移动 i 到最后（简化）
    # 可选 ORDER BY
    if i < len(tokens) and tokens[i][1].upper() == "ORDER":
        i += 1
        if i >= len(tokens) or tokens[i][1].upper() != "BY":
            raise SyntaxError("Missing BY after ORDER")
        i += 1
        if i >= len(tokens) or tokens[i][0] != "IDENT":
            raise SyntaxError("Missing column for ORDER BY")
        col = tokens[i][1]
        i += 1
        direction = "ASC"
        if i < len(tokens) and tokens[i][0] == "KEYWORD" and tokens[i][1].upper() in ("ASC","DESC"):
            direction = tokens[i][1].upper()
        ast.order_by = (col, direction)
    return ast

def parse_where(tokens, start):
    """递归解析条件表达式，返回嵌套字典"""
    # 简化实现：仅支持二元比较和 AND/OR，忽略括号优先级
    # 返回格式：{'op': 'AND', 'left': {...}, 'right': {...}} 或 {'col': col, 'op': op, 'val': val}
    # 这里实现一个简单版本，后续在 executor 中直接使用字符串评估
    # 为了简单，我们直接返回原始 tokens 片段，由 executor 动态 eval（注意安全）
    # 实际生产环境应使用安全评估，这里为了简洁，返回表达式字符串
    where_str = " ".join(t[1] for t in tokens[start:] if t[0] != "PUNCT" or t[1] != ";")
    return where_str   # 作为字符串，executor 中使用 eval(条件, {行字典})