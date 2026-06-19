import os
from dotenv import load_dotenv

load_dotenv()

# 尝试导入 groq，如果失败则使用 mock
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False
    print("Warning: groq not installed. Install with 'uv add groq'")

class LLMClient:
    def __init__(self, mock: bool = False):
        self.mock = mock or not HAS_GROQ
        if not self.mock:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                print("Warning: GROQ_API_KEY not set, using mock mode")
                self.mock = True
            else:
                self.client = Groq(api_key=api_key)
                self.model = "llama3-70b-8192"  # 免费快速

    def generate_sql(self, user_question: str, schema: str) -> str:
        if self.mock:
            # 返回基于规则的简单转换（演示用）
            return self._rule_based_sql(user_question, schema)
        # 调用真实 API
        system_prompt = """你是一个 SQL 专家。根据给定的表结构，将用户的自然语言问题转换为标准 SQL 查询。
只返回 SQL 语句，不要有任何解释或额外文字。"""
        user_prompt = f"表结构：{schema}\n用户问题：{user_question}\nSQL："
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            sql = completion.choices[0].message.content.strip()
            # 去除可能的多余标记
            if sql.startswith("```sql"):
                sql = sql[6:]
            if sql.endswith("```"):
                sql = sql[:-3]
            return sql
        except Exception as e:
            print(f"LLM error: {e}, falling back to rule-based")
            return self._rule_based_sql(user_question, schema)

    def _rule_based_sql(self, question: str, schema: str) -> str:
        # 极简规则，仅用于演示
        q = question.lower()
        if "所有" in q or "全部" in q:
            return "SELECT * FROM sales"
        if "大于" in q or ">" in q:
            # 尝试提取数字和字段
            return "SELECT * FROM sales WHERE sales_amount > 1000"  # demo
        if "总和" in q or "总计" in q:
            return "SELECT SUM(sales_amount) FROM sales"
        if "平均" in q:
            return "SELECT AVG(sales_amount) FROM sales"
        if "排序" in q or "降序" in q:
            return "SELECT * FROM sales ORDER BY sales_amount DESC"
        return "SELECT * FROM sales"