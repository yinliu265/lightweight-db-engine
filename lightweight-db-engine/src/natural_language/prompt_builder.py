def build_prompt(schema: str, user_question: str) -> str:
    """构建包含 schema 和用户问题的 prompt"""
    # 实际调用在 llm_client 中已经包含，这里仅提供辅助
    return f"表结构：{schema}\n用户问题：{user_question}\nSQL："