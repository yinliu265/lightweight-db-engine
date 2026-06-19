import re
from typing import List, Tuple

def tokenize(sql: str) -> List[Tuple[str, str]]:
    """将 SQL 字符串拆分为 (类型, 值) 的 token 列表"""
    sql = sql.strip()
    tokens = []
    # 匹配：关键字/标识符/数字/字符串/运算符/括号/逗号/分号
    patterns = [
        (r"\b(SELECT|FROM|WHERE|ORDER\s+BY|AND|OR|ASC|DESC|COUNT|SUM|AVG|MAX|MIN)\b", "KEYWORD"),
        (r"\*", "STAR"),
        (r"[><=!]=?", "OPERATOR"),
        (r"\d+(?:\.\d+)?", "NUMBER"),
        (r"'[^']*'", "STRING"),
        (r"[a-zA-Z_][a-zA-Z0-9_]*", "IDENT"),
        (r"[(),]", "PUNCT"),
        (r"\s+", "WHITESPACE"),
        (r";", "SEMICOLON"),
    ]
    pos = 0
    while pos < len(sql):
        match = None
        for pattern, typ in patterns:
            regex = re.compile(pattern, re.IGNORECASE)
            m = regex.match(sql, pos)
            if m:
                match = m
                token_val = m.group(0)
                if typ != "WHITESPACE":
                    tokens.append((typ, token_val))
                pos = m.end()
                break
        if not match:
            raise SyntaxError(f"Unexpected character at position {pos}: {sql[pos]}")
    return tokens