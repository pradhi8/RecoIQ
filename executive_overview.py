import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Executive Overview · RecoIQ",
    page_icon="📊",
    layout="wide",
)

# ── Design tokens ─────────────────────────────────────────────────────────────
DARK_BG       = "#0D1117"
PANEL_BG      = "#161B22"
PANEL_BORDER  = "#21262D"
ACCENT_TEAL   = "#39D0C8"
ACCENT_VIOLET = "#7C5CFC"
ACCENT_AMBER  = "#F0A500"
ACCENT_ROSE   = "#F75D7E"
TEXT_PRIMARY  = "#E6EDF3"
TEXT_MUTED    = "#8B949E"
FP_COLOR      = "#39D0C8"
IBCF_COLOR    = "#7C5CFC"

st.markdown(f"""
<style>
  html, body, [data-testid="stAppViewContainer"] {{
      background-color: {DARK_BG};
      color: {TEXT_PRIMARY};
      font-family: 'Inter', 'Segoe UI', sans-serif;
  }}
  [data-testid="stSidebar"] {{
      background-color: {PANEL_BG};
      border-right: 1px solid {PANEL_BORDER};
  }}
  [data-testid="stSidebar"] * {{ color: {TEXT_PRIMARY} !important; }}

  .page-eyebrow {{
      font-size: 0.68rem;
      font-weight: 600;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: {ACCENT_TEAL};
      margin-bottom: 4px;
  }}
  .page-title {{
      font-size: 1.8rem;
      font-weight: 800;
      color: {TEXT_PRIMARY};
      margin: 0 0 4px 0;
  }}
  .page-subtitle {{
      font-size: 0.85rem;
      color: {TEXT_MUTED};
      margin-bottom: 0;
  }}
  .section-header {{
      font-size: 0.7rem;
      font-weight: 600;
      color: {TEXT_MUTED};
      text-transform: uppercase;
      letter-spacing: 0.12em;
      border-bottom: 1px solid {PANEL_BORDER};
      padding-bottom: 6px;
      margin-bottom: 16px;
  }}
  .kpi-card {{
      background: {PANEL_BG};
      border: 1px solid {PANEL_BORDER};
      border-radius: 10px;
      padding: 20px 22px;
  }}
  .kpi-value {{
      font-size: 2.1rem;
      font-weight: 800;
      line-height: 1.1;
  }}
  .kpi-label {{
      font-size: 0.72rem;
      color: {TEXT_MUTED};
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-top: 4px;
  }}
  .kpi-delta {{
      font-size: 0.75rem;
      margin-top: 6px;
      font-weight: 600;
  }}
  .engine-card {{
      background: {PANEL_BG};
      border: 1px solid {PANEL_BORDER};
      border-radius: 10px;
      padding: 22px 24px;
  }}
  .engine-name {{
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 14px;
  }}
  .engine-stat-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 7px 0;
      border-bottom: 1px solid {PANEL_BORDER};
  }}
  .engine-stat-row:last-child {{ border-bottom: none; }}
  .engine-stat-label {{ font-size: 0.78rem; color: {TEXT_MUTED}; }}
  .engine-stat-value {{ font-size: 0.9rem; font-weight: 700; color: {TEXT_PRIMARY}; }}
  .chart-panel {{
      background: {PANEL_BG};
      border: 1px solid {PANEL_BORDER};
      border-radius: 10px;
      padding: 20px;
  }}
  div[data-testid="stPlotlyChart"] {{
      background: transparent !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── Data Loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_engine_comparison():
    return pd.read_csv(
        "data/recommendation_engine_comparison.csv"
    )


@st.cache_data(ttl=300, show_spinner=False)
def load_segment_fp():
    return pd.read_csv(
        "data/segment_performance_fp.csv"
    )


@st.cache_data(ttl=300, show_spinner=False)
def load_segment_ibcf():
    return pd.read_csv(
        "data/segment_performance_ibcf.csv"
    )


@st.cache_data(ttl=300, show_spinner=False)
def load_product_comparison():
    return pd.read_csv(
        "data/product_recommendation_comparison.csv"
    )


@st.cache_data(ttl=300, show_spinner=False)
def load_customer_360():
    df = pd.read_csv(
        "data/customer_360_enhanced.csv"
    )

    # Convert comma-separated product strings into Python lists
    for col in [
        "owned_products",
        "fp_recommendations",
        "ibcf_recommendations"
    ]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: (
                    [item.strip() for item in str(x).split(",")]
                    if pd.notna(x) and str(x).strip()
                    else []
                )
            )

    return df

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Loading platform data…"):
    try:
        eng_df   = load_engine_comparison()
        seg_fp   = load_segment_fp()
        seg_ibcf = load_segment_ibcf()
        prod_df  = load_product_comparison()
        c360     = load_customer_360()
        load_ok  = True
    except Exception as e:
        st.error(f"Data load failed: {e}")
        load_ok = False

if not load_ok:
    st.stop()

# ── Derive platform-level KPIs ────────────────────────────────────────────────
total_customers    = len(c360)
total_owned        = c360["owned_products"].apply(len).sum()
avg_owned          = c360["owned_products"].apply(len).mean()

fp_row   = eng_df[eng_df["engine"].str.contains("FP", case=False)].iloc[0] if not eng_df.empty else {}
ibcf_row = eng_df[eng_df["engine"].str.contains("IBCF", case=False, na=False)].iloc[0] if not eng_df.empty else {}

total_recs = int(eng_df["recommendation_count"].sum()) if "recommendation_count" in eng_df.columns else 0
avg_score_fp   = float(fp_row.get("average_score", 0))   if fp_row is not None and len(fp_row) else 0
avg_score_ibcf = float(ibcf_row.get("average_score", 0)) if ibcf_row is not None and len(ibcf_row) else 0

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='font-size:1.1rem;font-weight:800;color:{ACCENT_TEAL};margin-bottom:4px'>RecoIQ</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.7rem;color:{TEXT_MUTED};margin-bottom:24px'>Recommendation Intelligence Platform</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.72rem;color:{TEXT_MUTED}'>Platform scope</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.9rem;font-weight:700;color:{TEXT_PRIMARY}'>{total_customers} customers · {total_recs} recommendations</div>", unsafe_allow_html=True)
    st.markdown("---")
    top_n_products = st.slider("Top Products to Display", 5, 20, 10)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown('<div class="page-eyebrow">Platform Intelligence</div>', unsafe_allow_html=True)
st.markdown('<p class="page-title">Executive Overview</p>', unsafe_allow_html=True)
st.markdown(f'<p class="page-subtitle">Cross-engine performance across {total_customers} customers · Banking · Insurance · Telecom · Retail · FinTech · Wealth</p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, value, label, color=ACCENT_TEAL, delta=None):
    delta_html = f'<div class="kpi-delta" style="color:{ACCENT_TEAL}">{delta}</div>' if delta else ""
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-value" style="color:{color}">{value}</div>
      <div class="kpi-label">{label}</div>
      {delta_html}
    </div>""", unsafe_allow_html=True)

kpi(k1, f"{total_customers:,}",    "Total Customers",      ACCENT_TEAL)
kpi(k2, f"{total_recs:,}",         "Total Recommendations", ACCENT_VIOLET)
kpi(k3, f"{avg_owned:.1f}",        "Avg Products / Customer", ACCENT_AMBER)
kpi(k4, f"{avg_score_fp:.3f}",     "Avg FP-Growth Score",  FP_COLOR)
kpi(k5, f"{avg_score_ibcf:.3f}",   "Avg IBCF Score",       IBCF_COLOR)

st.markdown("<br>", unsafe_allow_html=True)

# ── Engine side-by-side cards ─────────────────────────────────────────────────
st.markdown('<div class="section-header">Engine Comparison</div>', unsafe_allow_html=True)
ec1, ec2 = st.columns(2)

def engine_card(col, row, name, color):
    if row is None or len(row) == 0:
        col.markdown(f'<div class="engine-card"><div class="engine-name" style="color:{color}">{name}</div><p style="color:{TEXT_MUTED}">No data.</p></div>', unsafe_allow_html=True)
        return
    rec_count  = int(row.get("recommendation_count", 0))
    cust_cov   = float(row.get("customer_coverage", 0))
    cat_cov    = float(row.get("catalog_coverage", 0))
    avg_sc     = float(row.get("average_score", 0))
    col.markdown(f"""
    <div class="engine-card">
      <div class="engine-name" style="color:{color}">⬡ {name}</div>
      <div class="engine-stat-row">
        <span class="engine-stat-label">Recommendations Generated</span>
        <span class="engine-stat-value">{rec_count:,}</span>
      </div>
      <div class="engine-stat-row">
        <span class="engine-stat-label">Customer Coverage</span>
        <span class="engine-stat-value">{cust_cov:.1%}</span>
      </div>
      <div class="engine-stat-row">
        <span class="engine-stat-label">Catalog Coverage</span>
        <span class="engine-stat-value">{cat_cov:.1%}</span>
      </div>
      <div class="engine-stat-row">
        <span class="engine-stat-label">Average Score</span>
        <span class="engine-stat-value">{avg_sc:.4f}</span>
      </div>
    </div>""", unsafe_allow_html=True)

engine_card(ec1, fp_row,   "FP-Growth",  FP_COLOR)
engine_card(ec2, ibcf_row, "IBCF",       IBCF_COLOR)

st.markdown("<br>", unsafe_allow_html=True)

# ── Segment performance chart ─────────────────────────────────────────────────
st.markdown('<div class="section-header">Recommendation Volume by Segment</div>', unsafe_allow_html=True)

seg_fp_clean   = seg_fp.copy()
seg_ibcf_clean = seg_ibcf.copy()
seg_fp_clean["engine"]   = "FP-Growth"
seg_ibcf_clean["engine"] = "IBCF"
seg_combined = pd.concat([seg_fp_clean, seg_ibcf_clean], ignore_index=True)

if "customer_segment" in seg_combined.columns and "recommendations_generated" in seg_combined.columns:
    fig_seg = go.Figure()
    for engine, color in [("FP-Growth", FP_COLOR), ("IBCF", IBCF_COLOR)]:
        subset = seg_combined[seg_combined["engine"] == engine].sort_values("customer_segment")
        fig_seg.add_trace(go.Bar(
            name=engine,
            x=subset["customer_segment"],
            y=subset["recommendations_generated"],
            marker_color=color,
            marker_line_width=0,
            text=subset["recommendations_generated"],
            textposition="outside",
            textfont=dict(color=TEXT_MUTED, size=11),
        ))
    fig_seg.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(font=dict(color=TEXT_PRIMARY), bgcolor="rgba(0,0,0,0)",
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_MUTED, size=11)),
        yaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
                   tickfont=dict(color=TEXT_MUTED), title=None),
        bargap=0.25,
        bargroupgap=0.08,
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_seg, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Avg score by segment ──────────────────────────────────────────────────────
if "avg_score" in seg_combined.columns:
    st.markdown('<div class="section-header">Average Score by Segment</div>', unsafe_allow_html=True)
    chart_l, chart_r = st.columns(2)

    for col, engine, color, df_s in [
        (chart_l, "FP-Growth", FP_COLOR,   seg_fp_clean),
        (chart_r, "IBCF",      IBCF_COLOR, seg_ibcf_clean),
    ]:
        if "avg_score" not in df_s.columns:
            continue
        df_s = df_s.sort_values("avg_score", ascending=True)
        fig = go.Figure(go.Bar(
            x=df_s["avg_score"],
            y=df_s["customer_segment"],
            orientation="h",
            marker_color=color,
            marker_line_width=0,
            text=df_s["avg_score"].round(4),
            textposition="outside",
            textfont=dict(color=TEXT_MUTED, size=10),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=260,
            margin=dict(l=10, r=60, t=30, b=10),
            title=dict(text=engine, font=dict(color=color, size=12), x=0),
            xaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
                       tickfont=dict(color=TEXT_MUTED, size=10), showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_PRIMARY, size=11)),
        )
        with col:
            st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# ── Top recommended products ──────────────────────────────────────────────────
st.markdown('<div class="section-header">Most Recommended Products</div>', unsafe_allow_html=True)

if not prod_df.empty and "product_name" in prod_df.columns:
    prod_df["total"] = prod_df.get("fp_count", 0) + prod_df.get("ibcf_count", 0)
    top_prods = prod_df.sort_values("total", ascending=False).head(top_n_products)
    top_prods = top_prods.sort_values("total", ascending=True)

    fig_prod = go.Figure()
    for col_name, color, label in [
        ("fp_count",   FP_COLOR,   "FP-Growth"),
        ("ibcf_count", IBCF_COLOR, "IBCF"),
    ]:
        if col_name in top_prods.columns:
            fig_prod.add_trace(go.Bar(
                name=label,
                x=top_prods[col_name],
                y=top_prods["product_name"],
                orientation="h",
                marker_color=color,
                marker_line_width=0,
            ))

    fig_prod.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=max(300, top_n_products * 30),
        margin=dict(l=10, r=30, t=10, b=10),
        legend=dict(font=dict(color=TEXT_PRIMARY), bgcolor="rgba(0,0,0,0)",
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
                   tickfont=dict(color=TEXT_MUTED), title=dict(text="Total Recommendations", font=dict(color=TEXT_MUTED, size=11))),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_PRIMARY, size=11)),
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_prod, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Ownership distribution ────────────────────────────────────────────────────
st.markdown('<div class="section-header">Products Owned — Distribution</div>', unsafe_allow_html=True)

ownership_counts = c360["owned_products"].apply(len)
fig_hist = go.Figure(go.Histogram(
    x=ownership_counts,
    nbinsx=12,
    marker_color=ACCENT_TEAL,
    marker_line_color=DARK_BG,
    marker_line_width=1.5,
    opacity=0.85,
))
fig_hist.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=240,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_MUTED),
               title=dict(text="Number of Products Owned", font=dict(color=TEXT_MUTED, size=11))),
    yaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
               tickfont=dict(color=TEXT_MUTED),
               title=dict(text="Customers", font=dict(color=TEXT_MUTED, size=11))),
    bargap=0.08,
)
st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)