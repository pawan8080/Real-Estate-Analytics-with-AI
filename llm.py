"""Text-to-SQL translation using Claude API, with safety guardrails."""
import os
import re
from anthropic import Anthropic
from database import get_schema

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """You are a SQL expert for a real estate analytics database.
Convert natural language questions into valid SQLite SELECT queries.

{schema}

Rules:
1. Output ONLY the SQL query. No explanation, no markdown, no code fences.
2. Use only SELECT statements. Never INSERT, UPDATE, DELETE, DROP, ALTER, or ATTACH.
3. Always use the table name `listings`.
4. For "recent" or "latest", order by listing_date DESC.
5. For averages on price or square_feet, use ROUND(AVG(...), 0).
6. When grouping, always include useful context columns.
7. Limit results to 100 rows unless the user asks for more or it's an aggregate.
8. Text comparisons should be case-insensitive: use LOWER() or COLLATE NOCASE.
"""

# Disallowed SQL keywords — anything that modifies data or structure
FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA|REPLACE|TRUNCATE)\b",
    re.IGNORECASE,
)


def is_safe_sql(sql: str) -> tuple[bool, str]:
    """Whitelist check: only allow single SELECT statements."""
    stripped = sql.strip().rstrip(";").strip()
    if not stripped.upper().startswith("SELECT") and not stripped.upper().startswith("WITH"):
        return False, "Query must start with SELECT or WITH."
    if ";" in stripped:
        return False, "Multiple statements are not allowed."
    if FORBIDDEN.search(stripped):
        return False, "Query contains forbidden keywords."
    return True, ""


def clean_sql_response(text: str) -> str:
    """Strip markdown fences and extra whitespace from LLM output."""
    text = text.strip()
    # Remove ```sql ... ``` or ``` ... ``` fences if the model added them
    text = re.sub(r"^```(?:sql)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_sql(question: str) -> str:
    """Convert a natural language question to SQL using Claude."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to your environment or .env file."
        )

    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT.format(schema=get_schema()),
        messages=[{"role": "user", "content": question}],
    )
    sql = clean_sql_response(message.content[0].text)
    return sql
