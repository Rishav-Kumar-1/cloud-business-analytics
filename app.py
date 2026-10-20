import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Cloud Analytics | Decision Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Visual theme
st.markdown("""
<style>
.block-container {padding-top: 1.3rem; padding-bottom: 2rem; max-width: 1500px;}
.hero {padding: 1.35rem 1.5rem; border-radius: 18px; background: linear-gradient(120deg,#10243A,#245B78); color: white; margin-bottom: 1.1rem;}
.hero h1 {font-size: 2rem; margin: 0 0 .35rem 0; color: white;}
.hero p {margin: 0; color: #D8EAF3; font-size: 1rem;}
.kpi {border: 1px solid rgba(128,128,128,.25); border-radius: 14px; padding: 14px 16px; background: rgba(128,128,128,.045);}
.kpi-label {font-size: .82rem; opacity: .78; margin-bottom: .35rem;}
.kpi-value {font-size: 1.55rem; font-weight: 700; letter-spacing: -.02em;}
.section-note {opacity: .72; font-size: .9rem;}
div[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.2); padding: 12px 14px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
FILES = {
    "DataServe India": "dataserve_india.csv",
    "Competitor Alpha": "competitor_alpha.csv",
    "Competitor Beta": "competitor_beta.csv",
}
MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
PALETTE = {"DataServe India":"#20A4A8", "Competitor Alpha":"#F4A261", "Competitor Beta":"#7B6DDB"}

@st.cache_data
def load_all():
    frames = {}
    for company, filename in FILES.items():
        path = os.path.join(DATA, filename)
        frame = pd.read_csv(path)
        frame["Company"] = company
        frames[company] = frame
    return frames

try:
    datasets = load_all()
except Exception as exc:
    st.error(f"Could not load the project CSV files: {exc}")
    st.info("Check that the data folder and the three CSV files are next to app.py.")
    st.stop()

all_data = pd.concat(datasets.values(), ignore_index=True)
st.markdown("""
<div class="hero">
  <h1>☁️ Cloud Analytics & Decision Intelligence</h1>
  <p>Interactive business performance dashboard · DataServe India vs Competitor Alpha and Competitor Beta</p>
</div>
""", unsafe_allow_html=True)

# Sidebar controls
st.sidebar.markdown("## 🎛️ Dashboard controls")
st.sidebar.caption("Choose the records to analyse. Benchmark cards always use the full supplied datasets.")
company_options = list(FILES.keys())
selected_companies = st.sidebar.multiselect("Companies", company_options, default=company_options)
available_months = [m for m in MONTH_ORDER if m in all_data["Month"].dropna().unique()]
selected_months = st.sidebar.multiselect("Months", available_months, default=available_months)
available_regions = sorted(all_data["Region"].dropna().astype(str).unique())
selected_regions = st.sidebar.multiselect("Regions", available_regions, default=available_regions)
available_units = sorted(all_data["Business_Unit"].dropna().astype(str).unique())
selected_units = st.sidebar.multiselect("Business units", available_units, default=available_units)
available_models = sorted(all_data["Cloud_Service_Model"].dropna().astype(str).unique())
selected_models = st.sidebar.multiselect("Cloud service models", available_models, default=available_models)

filtered = all_data[
    all_data["Company"].isin(selected_companies)
    & all_data["Month"].isin(selected_months)
    & all_data["Region"].astype(str).isin(selected_regions)
    & all_data["Business_Unit"].astype(str).isin(selected_units)
    & all_data["Cloud_Service_Model"].astype(str).isin(selected_models)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Select at least one company, month, region, business unit and service model.")
    st.stop()

def metrics(frame):
    volume = frame["Data_Volume_GB"].sum()
    cost = frame["Cloud_Cost_INR"].sum()
    return {
        "Records": len(frame),
        "Avg query time": frame["Avg_Query_Time_Sec"].mean(),
        "Avg uptime": frame["Uptime_Pct"].mean(),
        "Cost per GB": cost / volume if volume else 0,
        "Data quality": frame["Data_Quality_Score"].mean(),
        "Conversion": frame["Conversion_Rate_Pct"].mean(),
    }

m = metrics(filtered)
st.markdown("### 📌 Snapshot of selected data")
kcols = st.columns(6)
kpi_specs = [
    ("Records", f"{m['Records']:,}", "Filtered rows"),
    ("Avg query time", f"{m['Avg query time']:.2f} s", "Lower is faster"),
    ("Avg uptime", f"{m['Avg uptime']:.2f}%", "Availability indicator"),
    ("Cost per GB", f"₹{m['Cost per GB']:.2f}", "Total cost ÷ total GB"),
    ("Data quality", f"{m['Data quality']:.2f}", "Supplied score"),
    ("Conversion", f"{m['Conversion']:.2f}%", "Supplied conversion rate"),
]
for col, (label, value, caption) in zip(kcols, kpi_specs):
    with col:
        st.metric(label, value, help=caption)

st.markdown("---")
tab_overview, tab_compare, tab_explore, tab_data = st.tabs([
    "✨ Overview", "🏆 Competitor comparison", "🔎 Explore patterns", "📋 Data table"
])

with tab_overview:
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("#### Query performance over time")
        trend = filtered.groupby(["Month", "Company"], as_index=False).agg(
            Avg_Query_Time_Sec=("Avg_Query_Time_Sec","mean"),
            Avg_Conversion=("Conversion_Rate_Pct","mean")
        )
        trend["Month"] = pd.Categorical(trend["Month"], categories=MONTH_ORDER, ordered=True)
        trend = trend.sort_values("Month")
        fig = px.line(trend, x="Month", y="Avg_Query_Time_Sec", color="Company",
                      markers=True, color_discrete_map=PALETTE,
                      labels={"Avg_Query_Time_Sec":"Average query time (seconds)"},
                      template="plotly_white")
        fig.update_layout(legend_title_text="", margin=dict(l=5,r=5,t=15,b=5), height=360)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("#### Cloud cost mix")
        cost_mix = filtered.groupby("Cloud_Service_Model", as_index=False)["Cloud_Cost_INR"].sum()
        fig = px.pie(cost_mix, names="Cloud_Service_Model", values="Cloud_Cost_INR", hole=.58,
                     color_discrete_sequence=px.colors.qualitative.Bold, template="plotly_white")
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(l=5,r=5,t=15,b=5), height=360)
        st.plotly_chart(fig, use_container_width=True)
    left2, right2 = st.columns(2)
    with left2:
        st.markdown("#### Regional cloud spending")
        region_cost = filtered.groupby(["Region","Company"], as_index=False)["Cloud_Cost_INR"].sum()
        fig = px.bar(region_cost, x="Region", y="Cloud_Cost_INR", color="Company",
                     barmode="group", color_discrete_map=PALETTE,
                     labels={"Cloud_Cost_INR":"Total cloud cost (₹)"}, template="plotly_white")
        fig.update_layout(legend_title_text="", margin=dict(l=5,r=5,t=15,b=5), height=350)
        st.plotly_chart(fig, use_container_width=True)
    with right2:
        st.markdown("#### Data quality vs decision effectiveness")
        fig = px.scatter(filtered, x="Data_Quality_Score", y="Decision_Effectiveness_Score",
                         color="Company", size="Data_Volume_GB", hover_data=["Region","Month","Business_Unit"],
                         color_discrete_map=PALETTE, opacity=.68, template="plotly_white",
                         labels={"Data_Quality_Score":"Data quality score","Decision_Effectiveness_Score":"Decision effectiveness"})
        fig.update_layout(legend_title_text="", margin=dict(l=5,r=5,t=15,b=5), height=350)
        st.plotly_chart(fig, use_container_width=True)

with tab_compare:
    st.markdown("#### Company-level KPI benchmark")
    benchmark = []
    for name in selected_companies:
        d = datasets[name]
        volume = d["Data_Volume_GB"].sum()
        benchmark.append({
            "Company": name,
            "Records": len(d),
            "Avg query time (s)": d["Avg_Query_Time_Sec"].mean(),
            "Avg uptime (%)": d["Uptime_Pct"].mean(),
            "Cost per GB (₹)": d["Cloud_Cost_INR"].sum()/volume if volume else 0,
            "Data quality": d["Data_Quality_Score"].mean(),
            "Conversion (%)": d["Conversion_Rate_Pct"].mean(),
            "Satisfaction": d["Customer_Satisfaction_Score"].mean(),
            "Decision effectiveness": d["Decision_Effectiveness_Score"].mean(),
        })
    bench_df = pd.DataFrame(benchmark)
    st.dataframe(bench_df.round(2), use_container_width=True, hide_index=True)
    metric_choice = st.selectbox("Choose a KPI to compare", [
        "Avg query time (s)", "Avg uptime (%)", "Cost per GB (₹)", "Data quality",
        "Conversion (%)", "Satisfaction", "Decision effectiveness"
    ])
    fig = px.bar(bench_df, x="Company", y=metric_choice, color="Company",
                 color_discrete_map=PALETTE, text_auto=".2f", template="plotly_white")
    fig.update_layout(showlegend=False, margin=dict(l=5,r=5,t=15,b=5), height=380)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Query-time distribution")
    dist_df = all_data[all_data["Company"].isin(selected_companies)]
    fig = px.box(dist_df, x="Company", y="Avg_Query_Time_Sec", color="Company",
                 color_discrete_map=PALETTE, points="outliers", template="plotly_white",
                 labels={"Avg_Query_Time_Sec":"Query time (seconds)"})
    fig.update_layout(showlegend=False, margin=dict(l=5,r=5,t=15,b=5), height=380)
    st.plotly_chart(fig, use_container_width=True)

with tab_explore:
    st.markdown("#### Relationship explorer")
    c1, c2 = st.columns(2)
    numeric_cols = [
        "Data_Volume_GB","Query_Count","Avg_Query_Time_Sec","Cloud_Cost_INR","Uptime_Pct",
        "Dashboard_Users","Dashboard_Views","Data_Quality_Score","Conversion_Rate_Pct",
        "Customer_Satisfaction_Score","Optimization_Score","Storage_Utilization_Pct",
        "Decision_Effectiveness_Score"
    ]
    with c1:
        x_var = st.selectbox("X-axis", numeric_cols, index=numeric_cols.index("Data_Volume_GB"))
    with c2:
        y_var = st.selectbox("Y-axis", numeric_cols, index=numeric_cols.index("Cloud_Cost_INR"))
    fig = px.scatter(filtered, x=x_var, y=y_var, color="Company", size="Query_Count",
                     hover_data=["Region","Month","Cloud_Service_Model"], opacity=.7,
                     color_discrete_map=PALETTE, trendline="ols" if len(filtered) > 2 else None,
                     template="plotly_white")
    fig.update_layout(legend_title_text="", margin=dict(l=5,r=5,t=15,b=5), height=430)
    st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### KPI correlation heatmap")
        corr = filtered[numeric_cols].corr(numeric_only=True)
        fig = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
                        zmin=-1, zmax=1, template="plotly_white")
        fig.update_layout(margin=dict(l=5,r=5,t=15,b=5), height=500)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        st.markdown("#### Query-time histogram")
        fig = px.histogram(filtered, x="Avg_Query_Time_Sec", color="Company", barmode="overlay",
                           opacity=.72, color_discrete_map=PALETTE, nbins=25,
                           labels={"Avg_Query_Time_Sec":"Query time (seconds)"}, template="plotly_white")
        fig.update_layout(legend_title_text="", margin=dict(l=5,r=5,t=15,b=5), height=500)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Conversion by mining segment")
    segment = filtered.groupby(["Mining_Segment","Company"], as_index=False)["Conversion_Rate_Pct"].mean()
    fig = px.bar(segment, x="Mining_Segment", y="Conversion_Rate_Pct", color="Company",
                 barmode="group", color_discrete_map=PALETTE, text_auto=".2f",
                 labels={"Conversion_Rate_Pct":"Average conversion rate (%)"}, template="plotly_white")
    fig.update_layout(legend_title_text="", margin=dict(l=5,r=5,t=15,b=5), height=390)
    st.plotly_chart(fig, use_container_width=True)

with tab_data:
    st.markdown("#### Filtered records")
    st.caption(f"{len(filtered):,} rows match the current filters.")
    st.dataframe(filtered.drop(columns=["Company"], errors="ignore"), use_container_width=True, hide_index=True)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered records (CSV)", csv,
                       file_name="cloud_analytics_filtered_data.csv", mime="text/csv")
    st.markdown("#### Download company benchmark")
    if "bench_df" not in locals():
        benchmark = []
        for name in selected_companies:
            d = datasets[name]
            vol = d["Data_Volume_GB"].sum()
            benchmark.append({"Company":name,"Records":len(d),
                              "Avg query time (s)":d["Avg_Query_Time_Sec"].mean(),
                              "Avg uptime (%)":d["Uptime_Pct"].mean(),
                              "Cost per GB (₹)":d["Cloud_Cost_INR"].sum()/vol if vol else 0,
                              "Data quality":d["Data_Quality_Score"].mean(),
                              "Conversion (%)":d["Conversion_Rate_Pct"].mean()})
        bench_df = pd.DataFrame(benchmark)
    st.download_button("⬇️ Download benchmark KPIs (CSV)", bench_df.to_csv(index=False).encode("utf-8"),
                       file_name="company_benchmark_kpis.csv", mime="text/csv")

st.markdown("---")
st.markdown("### 💡 Decision support")
full_client = datasets["DataServe India"]
full_alpha = datasets["Competitor Alpha"]
full_beta = datasets["Competitor Beta"]
def cpg(frame):
    return frame["Cloud_Cost_INR"].sum()/frame["Data_Volume_GB"].sum()
client_q = full_client["Avg_Query_Time_Sec"].mean()
alpha_q = full_alpha["Avg_Query_Time_Sec"].mean()
beta_q = full_beta["Avg_Query_Time_Sec"].mean()
client_cost = cpg(full_client)
alpha_cost = cpg(full_alpha)
beta_cost = cpg(full_beta)
client_uptime = full_client["Uptime_Pct"].mean()
client_quality = full_client["Data_Quality_Score"].mean()
rec1, rec2, rec3 = st.columns(3)
with rec1:
    st.markdown("**⚡ Query speed**")
    st.write(f"DataServe average: **{client_q:.2f} seconds**.")
    if client_q > min(alpha_q,beta_q):
        st.write(f"Action: profile slow queries and pilot indexing/caching. Best competitor reference: {min(alpha_q,beta_q):.2f} seconds.")
    else:
        st.write("DataServe meets or beats the fastest competitor average on this metric.")
with rec2:
    st.markdown("**💸 Cloud cost**")
    st.write(f"DataServe: **₹{client_cost:.2f}/GB**.")
    if client_cost > min(alpha_cost,beta_cost):
        st.write(f"Action: review idle compute, storage tiers and workload scheduling. Lowest competitor reference: ₹{min(alpha_cost,beta_cost):.2f}/GB.")
    else:
        st.write("DataServe meets or beats the lowest competitor cost per GB.")
with rec3:
    st.markdown("**🛡️ Quality & reliability**")
    st.write(f"Uptime: **{client_uptime:.2f}%** · Data quality: **{client_quality:.2f}**.")
    st.write("Action: monitor availability, validate fields, detect duplicates and assign data ownership.")
st.caption("Method: averages are arithmetic means per record. Cost per GB = total cloud cost divided by total data volume. Benchmark comparisons are descriptive; workload differences may affect results and do not establish causation.")
