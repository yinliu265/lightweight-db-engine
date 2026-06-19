import struct
import pickle
from pathlib import Path
from typing import List, Dict, Any

def read_columnar(columns_to_read: List[str], input_dir: str) -> List[Dict]:
    """只读取指定的列，返回行列表"""
    in_path = Path(input_dir)
    with open(in_path / "metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    row_count = metadata["row_count"]
    col_data = {}
    for col in columns_to_read:
        col_path = in_path / f"{col}.bin"
        if not col_path.exists():
            raise FileNotFoundError(f"Column {col} not found")
        values = []
        with open(col_path, "rb") as f:
            for _ in range(row_count):
                typ = struct.unpack("B", f.read(1))[0]
                if typ == 0:  # NULL
                    values.append(None)
                elif typ == 1:  # int
                    val = struct.unpack("q", f.read(8))[0]
                    values.append(val)
                elif typ == 2:  # float
                    val = struct.unpack("d", f.read(8))[0]
                    values.append(val)
                elif typ == 3:  # string
                    length = struct.unpack("I", f.read(4))[0]
                    val = f.read(length).decode("utf-8")
                    values.append(val)
                else:
                    raise ValueError(f"Unknown type {typ}")
        col_data[col] = values
    # 重构行
    rows = []
    for i in range(row_count):
        row = {col: col_data[col][i] for col in columns_to_read}
        rows.append(row)
    return rows