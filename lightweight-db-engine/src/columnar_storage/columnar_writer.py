import struct
import pickle
from pathlib import Path
from typing import List, Dict, Any

def write_columnar(data: List[Dict], columns: List[str], output_dir: str):
    """将数据按列存储到二进制文件"""
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)
    # 保存列元数据
    metadata = {"columns": columns, "row_count": len(data)}
    with open(out_path / "metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)
    # 为每列创建文件
    for col in columns:
        # 收集该列所有值
        col_values = [row.get(col) for row in data]
        # 简单编码：前4字节表示每个值的类型和长度，然后存储数据
        with open(out_path / f"{col}.bin", "wb") as f:
            for val in col_values:
                if val is None:
                    f.write(struct.pack("B", 0))  # 类型0：NULL
                elif isinstance(val, int):
                    f.write(struct.pack("B", 1))  # 类型1：int
                    f.write(struct.pack("q", val))
                elif isinstance(val, float):
                    f.write(struct.pack("B", 2))  # 类型2：float
                    f.write(struct.pack("d", val))
                elif isinstance(val, str):
                    encoded = val.encode("utf-8")
                    f.write(struct.pack("B", 3))  # 类型3：string
                    f.write(struct.pack("I", len(encoded)))
                    f.write(encoded)
                else:
                    raise TypeError(f"Unsupported type: {type(val)}")