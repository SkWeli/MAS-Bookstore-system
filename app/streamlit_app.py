import pandas as pd
import altair as alt
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="MAS Bookstore Dashboard", layout="wide")

st.title("📚 MAS Bookstore — Simulation Dashboard")

events_path = Path("report/events.csv")
ts_path = Path("report/inventory_timeseries.csv")

if not events_path.exists() or not ts_path.exists():
    st.warning("Run the simulation first to generate CSVs (events.csv and inventory_timeseries.csv).")
    st.code("python app/run.py")
    st.stop()

events = pd.read_csv(events_path)
ts = pd.read_csv(ts_path)

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
total_purchases = (events["type"] == "purchase_ok").sum()
restocks = (events["type"] == "restock").sum()
fails = (events["type"] == "purchase_fail").sum()
unique_books = events.loc[events["type"] == "purchase_ok", "book"].nunique()

col1.metric("✅ Purchases", int(total_purchases))
col2.metric("🔄 Restocks", int(restocks))
col3.metric("❌ Failed Attempts", int(fails))
col4.metric("📖 Books Purchased", int(unique_books))

st.markdown("---")

# --- Inventory over time ---
st.subheader("Inventory Levels Over Time")
melted = ts.melt(id_vars=["step"], var_name="inventory", value_name="qty")
line = alt.Chart(melted).mark_line().encode(
    x="step:Q",
    y="qty:Q",
    color="inventory:N",
    tooltip=["step", "inventory", "qty"]
).properties(height=300)
st.altair_chart(line, use_container_width=True)

# --- Purchases per step ---
st.subheader("Purchases per Step")
purch = events[events["type"] == "purchase_ok"].groupby("step").size().reset_index(name="count")
bar = alt.Chart(purch).mark_bar().encode(
    x="step:Q",
    y="count:Q",
    tooltip=["step", "count"]
).properties(height=250)
st.altair_chart(bar, use_container_width=True)

# --- Restocks table ---
st.subheader("Restock Events")
restock_tbl = events[events["type"] == "restock"].copy()
st.dataframe(restock_tbl, use_container_width=True)

st.caption("Tip: Re-run the simulation to refresh data; refresh this page to update charts.")
