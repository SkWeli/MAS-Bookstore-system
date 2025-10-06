# dashboard.py
import os
import shutil
from pathlib import Path

import pandas as pd
import altair as alt
import streamlit as st

# Allow importing from the "app" folder (model.py lives there)
import sys
sys.path.append(str(Path(__file__).resolve().parent / "app"))

from model import BookstoreModel  # noqa: E402


st.set_page_config(page_title="MAS Bookstore Dashboard", layout="wide")
st.title("📚 MAS Bookstore - Simulation Dashboard")

# --------------------------------------------------------------------
# Controls: pick simulation parameters and run it
# --------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Simulation Controls")

    n_customers = st.number_input("Number of customers(Max: 12)", min_value=1, max_value=12, value=12, step=1)
    n_employees = st.number_input("Number of employees(Max: 2)", min_value=1, max_value=2, value=2, step=1)
    steps = st.number_input("Steps", min_value=1, max_value=1000, value=40, step=1)
    restock_threshold = st.number_input("Restock threshold", min_value=1, max_value=10_000, value=10, step=1)
    restock_target = st.number_input("Restock target", min_value=1, max_value=10_000, value=30, step=1)
    seed = st.number_input("Seed (optional, -1 for random)", min_value=-1, max_value=1_000_000, value=42, step=1)

    run_clicked = st.button("▶️ Run Simulation", type="primary", use_container_width=True)

# Paths to generated CSVs
events_path = Path("report/events.csv")
ts_path = Path("report/inventory_timeseries.csv")

def run_simulation():
    """Run the MAS simulation and write CSVs into report/."""
    # Clean report directory so we don't mix old/new data
    report_dir = Path("report")
    if report_dir.exists():
        shutil.rmtree(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    # Instantiate and run the model
    kwargs = dict(
        n_customers=int(n_customers),
        n_employees=int(n_employees),
        steps=int(steps),
        restock_threshold=int(restock_threshold),
        restock_target=int(restock_target),
    )
    if seed >= 0:
        kwargs["seed"] = int(seed)

    m = BookstoreModel(**kwargs)
    m.run()  # writes report/events.csv and report/inventory_timeseries.csv

    return True

# If user clicks "Run Simulation", execute it
if run_clicked:
    with st.spinner("Running simulation..."):
        ok = run_simulation()
    if ok and events_path.exists() and ts_path.exists():
        st.success("Simulation complete! Charts are updated below.")

# --------------------------------------------------------------------
# Load data (if present)
# --------------------------------------------------------------------
if not events_path.exists() or not ts_path.exists():
    st.info("Run the simulation from the left sidebar to generate CSVs (events.csv and inventory_timeseries.csv).")
    st.stop()

events = pd.read_csv(events_path)
ts = pd.read_csv(ts_path)

# Normalize column names
events.columns = [c.strip() for c in events.columns]
ts.columns = [c.strip() for c in ts.columns]

# --------------------------------------------------------------------
# KPI cards
# --------------------------------------------------------------------
# Prefer explicit 'purchase_ok' if present; otherwise use 'purchase_request'
purchase_type = "purchase_ok" if (events["type"] == "purchase_ok").any() else "purchase_request"
total_purchases = int((events["type"] == purchase_type).sum())
restocks = int((events["type"] == "restock").sum())

# Steps: time series includes step snapshots; max(step) equals steps executed
if "step" in ts.columns and not ts.empty:
    steps_executed = int(ts["step"].max())
else:
    steps_executed = 0

unique_books = (
    events.loc[events["type"] == purchase_type, "book"].nunique()
    if "book" in events.columns else 0
)
num_customers = (
    events.loc[events["type"] == purchase_type, "customer"].nunique()
    if "customer" in events.columns else 0
)
num_employees = events["employee"].nunique() if "employee" in events.columns else 0

# Row 1
k1, k2, k3, k4 = st.columns(4)
k1.metric("✅ Purchases", total_purchases)
k2.metric("🔄 Restocks", restocks)
k3.metric("⏱️ Simulation Steps", steps_executed)
k4.metric("📖 Books Purchased", int(unique_books))

# Row 2
k5, k6 = st.columns(2)
k5.metric("👥 Customers", int(num_customers))
k6.metric("🧑‍💼 Employees", int(num_employees))

st.markdown("---")

# --------------------------------------------------------------------
# Build inventory → book title mapping (from restock logs)
# --------------------------------------------------------------------
inv_name_col = "inventory"
book_title_col = "book"

title_map = {}
if {"type", inv_name_col, book_title_col}.issubset(events.columns):
    title_map = (
        events[events["type"] == "restock"]
        [[inv_name_col, book_title_col]]
        .dropna()
        .drop_duplicates(subset=[inv_name_col])
        .set_index(inv_name_col)[book_title_col]
        .to_dict()
    )

# --------------------------------------------------------------------
# Inventory levels over time (line chart)
# --------------------------------------------------------------------
st.subheader("Inventory Levels Over Time")

if "step" in ts.columns:
    melted = ts.melt(id_vars=["step"], var_name=inv_name_col, value_name="qty")
    melted["series"] = melted[inv_name_col].map(title_map).fillna(melted[inv_name_col])

    choices = sorted(melted["series"].unique())
    default_sel = choices[:min(1, len(choices))]
    selected = st.multiselect("Filter inventories/books", options=choices, default=default_sel)

    base = alt.Chart(melted).transform_filter(
        alt.FieldOneOfPredicate(field="series", oneOf=selected) if selected else alt.datum.series != ""
    )

    line = base.mark_line().encode(
        x=alt.X("step:Q", title="Step"),
        y=alt.Y("qty:Q", title="Quantity"),
        color=alt.Color("series:N", title="Inventory / Book"),
        tooltip=["step", alt.Tooltip("series:N", title="Series"), alt.Tooltip("qty:Q", title="Qty")],
    ).properties(height=320)

    st.altair_chart(line, use_container_width=True)
else:
    st.info("`inventory_timeseries.csv` has no 'step' column — cannot plot time series.")

# --------------------------------------------------------------------
# Purchases per step (bar)
# --------------------------------------------------------------------
st.subheader("Purchases per Step")

if {"type", "step"}.issubset(events.columns):
    purch = (
        events[events["type"] == purchase_type]
        .groupby("step")
        .size()
        .reset_index(name="count")
        .sort_values("step")
    )
    bar = alt.Chart(purch).mark_bar().encode(
        x=alt.X("step:Q", title="Step"),
        y=alt.Y("count:Q", title="Purchases"),
        tooltip=["step", "count"],
    ).properties(height=260)
    st.altair_chart(bar, use_container_width=True)
else:
    st.info("Events CSV missing 'step' and/or 'type'; cannot plot purchases per step.")

# --------------------------------------------------------------------
# Current stock snapshot (last step)
# --------------------------------------------------------------------
st.subheader("Current Stock (last step)")
if "step" in ts.columns:
    last_row = ts.sort_values("step").tail(1)
    snapshot = last_row.drop(columns=["step"]).T.reset_index()
    snapshot.columns = [inv_name_col, "qty"]
    snapshot["book"] = snapshot[inv_name_col].map(title_map).fillna(snapshot[inv_name_col])
    snapshot = snapshot[["book", inv_name_col, "qty"]].sort_values("qty", ascending=False)
    st.dataframe(snapshot, use_container_width=True, height=360)
else:
    st.info("`inventory_timeseries.csv` has no 'step' column — cannot compute current snapshot.")

# --------------------------------------------------------------------
# Restock events (clean table)
# --------------------------------------------------------------------
st.subheader("Restock Events")
restock_cols_pref = ["step", "employee", "book", "inventory", "qty", "after_qty"]
restock_cols = [c for c in restock_cols_pref if c in events.columns]
restock_tbl = events[events["type"] == "restock"][restock_cols].sort_values(
    ["step"] + (["employee"] if "employee" in restock_cols else [])
)
st.dataframe(restock_tbl, use_container_width=True)

# --------------------------------------------------------------------
# Top books & top customers
# --------------------------------------------------------------------
st.markdown("---")
st.subheader("Top Books & Top Customers")

cA, cB = st.columns(2)

if {"type", "book"}.issubset(events.columns):
    top_books = (
        events[events["type"] == purchase_type]
        .groupby("book").size().reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(15)
    )
    with cA:
        st.markdown("**Top Books (by purchases)**")
        st.altair_chart(
            alt.Chart(top_books).mark_bar().encode(
                x=alt.X("count:Q", title="Purchases"),
                y=alt.Y("book:N", sort="-x", title="Book"),
                tooltip=["book", "count"],
            ).properties(height=420),
            use_container_width=True,
        )
else:
    with cA:
        st.info("No 'book' in events; cannot compute top books.")

if {"type", "customer"}.issubset(events.columns):
    top_customers = (
        events[events["type"] == purchase_type]
        .groupby("customer").size().reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(15)
    )
    with cB:
        st.markdown("**Top Customers (by purchases)**")
        st.altair_chart(
            alt.Chart(top_customers).mark_bar().encode(
                x=alt.X("count:Q", title="Purchases"),
                y=alt.Y("customer:N", sort="-x", title="Customer"),
                tooltip=["customer", "count"],
            ).properties(height=420),
            use_container_width=True,
        )
else:
    with cB:
        st.info("No 'customer' in events; cannot compute top customers.")

st.caption("Tip: set parameters at left, click **Run Simulation**, then scroll through the updated results.")
