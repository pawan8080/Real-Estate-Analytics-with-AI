"""AskEstate - Natural language analytics for real estate data."""
import streamlit as st
import plotly.express as px
from database import init_db, run_query, get_schema
from llm import generate_sql, is_safe_sql

st.set_page_config(page_title="AskEstate", page_icon="🏡", layout="wide")

# Initialize DB on first load
init_db()

# Session state for query history
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- Sidebar ----------
with st.sidebar:
    st.title("🏡 AskEstate")
    st.caption("Natural language analytics for real estate data")

    st.subheader("Try these examples")
    examples = [
        "What's the average price per square foot by city?",
        "Show me the 10 most expensive condos in Downtown",
        "How many properties sold in each neighborhood last year?",
        "What's the average days on market by property type?",
        "Compare median prices of houses built before 2000 vs after",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state.pending_question = ex

    st.divider()
    st.subheader("Query history")
    if not st.session_state.history:
        st.caption("No queries yet.")
    else:
        for i, q in enumerate(reversed(st.session_state.history[-10:])):
            st.caption(f"{len(st.session_state.history) - i}. {q[:60]}")

    st.divider()
    with st.expander("Database schema"):
        st.code(get_schema(), language="text")

# ---------- Main ----------
st.header("Ask a question about real estate data")
st.caption(
    "This app translates plain English questions into SQL using Claude, runs them "
    "against a 2,000-row real estate database, and visualizes the result."
)

default_q = st.session_state.pop("pending_question", "")
question = st.text_input(
    "Your question",
    value=default_q,
    placeholder="e.g. What's the average price of 3-bedroom houses in Denver?",
)

if st.button("Ask", type="primary") and question.strip():
    with st.spinner("Generating SQL..."):
        try:
            sql = generate_sql(question)
        except Exception as e:
            st.error(f"LLM error: {e}")
            st.stop()

    safe, reason = is_safe_sql(sql)
    if not safe:
        st.error(f"Generated query rejected by safety check: {reason}")
        st.code(sql, language="sql")
        st.stop()

    st.session_state.history.append(question)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Generated SQL")
        st.code(sql, language="sql")

    with st.spinner("Running query..."):
        try:
            df = run_query(sql)
        except Exception as e:
            st.error(f"Query failed: {e}")
            st.stop()

    with col2:
        st.subheader("Summary")
        st.metric("Rows returned", len(df))
        if len(df) > 0:
            st.metric("Columns", len(df.columns))

    st.subheader("Results")
    st.dataframe(df, use_container_width=True)

    # Auto-chart: if we have 1 categorical + 1 numeric column, make a bar chart
    if len(df) > 0 and len(df.columns) == 2:
        cat_col, num_col = df.columns[0], df.columns[1]
        if df[num_col].dtype.kind in "iuf":
            st.subheader("Visualization")
            fig = px.bar(df, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
            st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption(
    "Built with Streamlit, SQLite, and Anthropic Claude. "
    "Source on GitHub."
)
