from typing import Dict, List, Any

class HashIndex:
    def __init__(self, column: str):
        self.column = column
        self.index_map: Dict[Any, List[int]] = {}  # value -> list of row indices

    def build(self, data: List[Dict]):
        """从数据列表构建哈希索引"""
        self.index_map.clear()
        for idx, row in enumerate(data):
            val = row.get(self.column)
            if val is not None:
                if val not in self.index_map:
                    self.index_map[val] = []
                self.index_map[val].append(idx)

    def get_rows(self, value: Any, full_data: List[Dict]) -> List[Dict]:
        """根据索引值返回对应的行列表"""
        indices = self.index_map.get(value, [])
        return [full_data[i] for i in indices]