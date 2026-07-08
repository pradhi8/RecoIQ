import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Segment Analytics · RecoIQ",
    page_icon="🎯",
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
ACCENT_GREEN  = "#3FB950"
TEXT_PRIMARY  = "#E6EDF3"
TEXT_MUTED    = "#8B949E"
FP_COLOR      = "#39D0C8"
IBCF_COLOR    = "#7C5CFC"

SEGMENT_COLORS = {
    "Young Digital User":   "#39D0C8",
    "Working Professional": "#7C5CFC",
    "Family Builder":       "#F0A500",
    "Wealth Creator":       "#3FB950",
    "Retirement Planner":   "#F75D7E",
}
DEFAULT_COLOR = "#8B949E"

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
  div[data-baseweb="select"] > div {{
      background-color: {PANEL_BG} !important;
      border: 1px solid {PANEL_BORDER} !important;
      color: {TEXT_PRIMARY} !important;
  }}
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
      padding: 18px 22px;
  }}
  .kpi-value {{
      font-size: 1.9rem;
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
  .kpi-sub {{
      font-size: 0.72rem;
      color: {TEXT_MUTED};
      margin-top: 5px;
  }}
  .chart-panel {{
      background: {PANEL_BG};
      border: 1px solid {PANEL_BORDER};
      border-radius: 10px;
      padding: 20px;
  }}
  .seg-card {{
      background: {PANEL_BG};
      border: 1px solid {PANEL_BORDER};
      border-radius: 10px;
      padding: 20px 22px;
      margin-bottom: 12px;
  }}
  .seg-card-name {{
      font-size: 0.9rem;
      font-weight: 700;
      margin-bottom: 12px;
  }}
  .seg-stat-row {{
      display: flex;
      justify-content: space-between;
      padding: 6px 0;
      border-bottom: 1px solid {PANEL_BORDER};
      font-size: 0.8rem;
  }}
  .seg-stat-row:last-child {{ border-bottom: none; }}
  .seg-stat-label {{ color: {TEXT_MUTED}; }}
  .seg-stat-value {{ font-weight: 700; color: {TEXT_PRIMARY}; }}
  .chip-grid {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
  .chip {{
      background: rgba(255,255,255,0.05);
      border: 1px solid {PANEL_BORDER};
      border-radius: 6px;
      padding: 4px 10px;
      font-size: 0.74rem;
      color: {TEXT_PRIMARY};
  }}
  .profile-table {{
      background: {PANEL_BG};
      border: 1px solid {PANEL_BORDER};
      border-radius: 10px;
      padding: 20px;
      width: 100%;
  }}
  div[data-testid="stPlotlyChart"] {{ background: transparent !important; }}
</style>
""", unsafe_allow_html=True)

# ── Data Loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_customer_360():
    df = pd.read_csv(
        "data/customer_360_enhanced.csv"
    )

    # Convert comma-separated product strings into lists
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
def load_all_recommendations():
    return pd.read_csv(
        "data/all_recommendations.csv"
    )

with st.spinner("Loading segment data…"):
    try:
        c360     = load_customer_360()
        seg_fp   = load_segment_fp()
        seg_ibcf = load_segment_ibcf()
        all_recs = load_all_recommendations()
        load_ok  = True
    except Exception as e:
        st.error(f"Data load failed: {e}")
        load_ok = False

if not load_ok:
    st.stop()

# ── Derived segment stats ─────────────────────────────────────────────────────
c360["n_owned"]    = c360["owned_products"].apply(len)
c360["n_fp_recs"]  = c360["fp_recommendations"].apply(len)
c360["n_ibcf_recs"]= c360["ibcf_recommendations"].apply(len)

seg_profile = c360.groupby("customer_segment").agg(
    customer_count  = ("customer_id",    "count"),
    avg_age         = ("age",            "mean"),
    avg_income      = ("annual_income",  "mean"),
    avg_tenure      = ("tenure_months",  "mean"),
    avg_engagement  = ("engagement_score","mean"),
    avg_risk        = ("risk_score",     "mean"),
    avg_owned       = ("n_owned",        "mean"),
    avg_fp_recs     = ("n_fp_recs",      "mean"),
    avg_ibcf_recs   = ("n_ibcf_recs",   "mean"),
).reset_index()

segments = sorted(c360["customer_segment"].dropna().unique().tolist())

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='font-size:1.1rem;font-weight:800;color:{ACCENT_TEAL};margin-bottom:4px'>RecoIQ</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.7rem;color:{TEXT_MUTED};margin-bottom:24px'>Recommendation Intelligence Platform</div>", unsafe_allow_html=True)
    st.markdown("---")
    selected_seg = st.selectbox("Focus Segment", ["All Segments"] + segments)
    st.markdown("---")
    top_n_products = st.slider("Top Products per Segment", 3, 10, 5)
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.72rem;color:{TEXT_MUTED}'>Total segments</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1.3rem;font-weight:800;color:{ACCENT_TEAL}'>{len(segments)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.72rem;color:{TEXT_MUTED};margin-top:8px'>Total customers</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1.3rem;font-weight:800;color:{ACCENT_TEAL}'>{len(c360):,}</div>", unsafe_allow_html=True)

# filter
if selected_seg != "All Segments":
    view_c360    = c360[c360["customer_segment"] == selected_seg]
    view_profile = seg_profile[seg_profile["customer_segment"] == selected_seg]
    view_segs    = [selected_seg]
else:
    view_c360    = c360
    view_profile = seg_profile
    view_segs    = segments

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown('<div class="page-eyebrow">Segment Intelligence</div>', unsafe_allow_html=True)
st.markdown('<p class="page-title">Segment Analytics</p>', unsafe_allow_html=True)
st.markdown(f'<p class="page-subtitle">Behavioural profiles, ownership patterns, and recommendation performance across {len(segments)} customer segments</p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── KPI strip ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, value, label, color=ACCENT_TEAL, sub=None):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-value" style="color:{color}">{value}</div>
      <div class="kpi-label">{label}</div>
      {sub_html}
    </div>""", unsafe_allow_html=True)

kpi(k1, f"{len(view_c360):,}",                         "Customers",          ACCENT_TEAL)

kpi(k2, f"{view_c360['age'].mean():.0f}",              "Avg Age",            ACCENT_VIOLET)

kpi(k3, f"₹{view_c360['annual_income'].mean():,.0f}",  "Avg Annual Income",  ACCENT_AMBER)

kpi(k4, f"{view_c360['engagement_score'].mean():.2f}", "Avg Engagement",     ACCENT_GREEN)

kpi(k5, f"{view_c360['n_owned'].mean():.1f}",          "Avg Products Owned", ACCENT_ROSE)

st.markdown("<br>", unsafe_allow_html=True)

# ── Segment size + avg owned side by side ─────────────────────────────────────
st.markdown('<div class="section-header">Segment Size & Ownership Depth</div>', unsafe_allow_html=True)
sz_l, sz_r = st.columns(2)

seg_colors = [SEGMENT_COLORS.get(s, DEFAULT_COLOR) for s in view_profile["customer_segment"]]

with sz_l:
    fig_size = go.Figure(go.Bar(
        x=view_profile["customer_segment"],
        y=view_profile["customer_count"],
        marker_color=seg_colors,
        marker_line_width=0,
        text=view_profile["customer_count"],
        textposition="outside",
        textfont=dict(color=TEXT_MUTED, size=11),
    ))
    fig_size.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=10, r=10, t=30, b=10),
        title=dict(text="Customers per Segment", font=dict(color=TEXT_MUTED, size=12), x=0),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_MUTED, size=10)),
        yaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False, tickfont=dict(color=TEXT_MUTED)),
        showlegend=False,
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_size, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with sz_r:
    fig_owned = go.Figure(go.Bar(
        x=view_profile["customer_segment"],
        y=view_profile["avg_owned"].round(2),
        marker_color=seg_colors,
        marker_line_width=0,
        text=view_profile["avg_owned"].round(2),
        textposition="outside",
        textfont=dict(color=TEXT_MUTED, size=11),
    ))
    fig_owned.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=10, r=10, t=30, b=10),
        title=dict(text="Avg Products Owned per Segment", font=dict(color=TEXT_MUTED, size=12), x=0),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_MUTED, size=10)),
        yaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False, tickfont=dict(color=TEXT_MUTED)),
        showlegend=False,
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_owned, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Engagement & risk scatter ─────────────────────────────────────────────────
st.markdown('<div class="section-header">Engagement vs Risk · Customer Distribution</div>', unsafe_allow_html=True)

fig_scatter = go.Figure()
for seg in view_segs:
    subset = view_c360[view_c360["customer_segment"] == seg]
    color  = SEGMENT_COLORS.get(seg, DEFAULT_COLOR)
    fig_scatter.add_trace(go.Scatter(
        x=subset["engagement_score"],
        y=subset["risk_score"],
        mode="markers",
        name=seg,
        marker=dict(color=color, size=7, opacity=0.65, line=dict(width=0)),
        hovertemplate=(
            f"<b>{seg}</b><br>"
            "Engagement: %{x:.2f}<br>"
            "Risk: %{y:.2f}<extra></extra>"
        ),
    ))
fig_scatter.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=360,
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(font=dict(color=TEXT_PRIMARY, size=11), bgcolor="rgba(0,0,0,0)",
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
               tickfont=dict(color=TEXT_MUTED),
               title=dict(text="Engagement Score", font=dict(color=TEXT_MUTED, size=11))),
    yaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
               tickfont=dict(color=TEXT_MUTED),
               title=dict(text="Risk Score", font=dict(color=TEXT_MUTED, size=11))),
)
st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Income & tenure by segment ────────────────────────────────────────────────
st.markdown('<div class="section-header">Income & Tenure by Segment</div>', unsafe_allow_html=True)
inc_l, inc_r = st.columns(2)

with inc_l:
    fig_inc = go.Figure(go.Bar(
        x=view_profile["customer_segment"],
        y=view_profile["avg_income"],
        marker_color=seg_colors,
        marker_line_width=0,
        text=view_profile["avg_income"].apply(lambda v: f"₹{v:,.0f}"),
        textposition="outside",
        textfont=dict(color=TEXT_MUTED, size=10),
    ))
    fig_inc.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=10, r=10, t=30, b=10),
        title=dict(text="Avg Annual Income", font=dict(color=TEXT_MUTED, size=12), x=0),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_MUTED, size=10)),
        yaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
                   tickfont=dict(color=TEXT_MUTED),
                   tickprefix="₹", tickformat=",.0f"),
        showlegend=False,
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_inc, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with inc_r:
    fig_ten = go.Figure(go.Bar(
        x=view_profile["customer_segment"],
        y=view_profile["avg_tenure"].round(1),
        marker_color=seg_colors,
        marker_line_width=0,
        text=view_profile["avg_tenure"].round(1),
        textposition="outside",
        textfont=dict(color=TEXT_MUTED, size=10),
    ))
    fig_ten.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=10, r=10, t=30, b=10),
        title=dict(text="Avg Tenure (months)", font=dict(color=TEXT_MUTED, size=12), x=0),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_MUTED, size=10)),
        yaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False, tickfont=dict(color=TEXT_MUTED)),
        showlegend=False,
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_ten, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Avg recs per engine per segment ──────────────────────────────────────────
st.markdown('<div class="section-header">Average Recommendations per Customer · by Segment & Engine</div>', unsafe_allow_html=True)

fig_avgrec = go.Figure()
for col_name, color, label in [("avg_fp_recs", FP_COLOR, "FP-Growth"), ("avg_ibcf_recs", IBCF_COLOR, "IBCF")]:
    fig_avgrec.add_trace(go.Bar(
        name=label,
        x=view_profile["customer_segment"],
        y=view_profile[col_name].round(2),
        marker_color=color,
        marker_line_width=0,
        text=view_profile[col_name].round(2),
        textposition="outside",
        textfont=dict(color=TEXT_MUTED, size=10),
    ))
fig_avgrec.update_layout(
    barmode="group",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=300,
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(font=dict(color=TEXT_PRIMARY), bgcolor="rgba(0,0,0,0)",
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_MUTED, size=11)),
    yaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False, tickfont=dict(color=TEXT_MUTED)),
    bargap=0.25, bargroupgap=0.08,
)
st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
st.plotly_chart(fig_avgrec, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Top recommended products per segment ──────────────────────────────────────
st.markdown('<div class="section-header">Top Recommended Products per Segment</div>', unsafe_allow_html=True)

if not all_recs.empty and "engine" in all_recs.columns and "customer_id" in all_recs.columns:
    recs_with_seg = all_recs.merge(
        c360[["customer_id", "customer_segment"]], on="customer_id", how="left"
    )
    for seg in view_segs:
        color = SEGMENT_COLORS.get(seg, DEFAULT_COLOR)
        seg_recs = recs_with_seg[recs_with_seg["customer_segment"] == seg]
        if seg_recs.empty:
            continue

        col_l, col_r = st.columns(2)
        for col_widget, engine, eng_color in [(col_l, "FP-Growth", FP_COLOR), (col_r, "IBCF", IBCF_COLOR)]:
            eng_recs = seg_recs[seg_recs["engine"] == engine]
            if "product_name" in eng_recs.columns:
                top_prods = (
                    eng_recs.groupby("product_name")
                    .size().reset_index(name="count")
                    .sort_values("count", ascending=False)
                    .head(top_n_products)
                    .sort_values("count", ascending=True)
                )
                fig = go.Figure(go.Bar(
                    x=top_prods["count"],
                    y=top_prods["product_name"],
                    orientation="h",
                    marker_color=eng_color,
                    marker_line_width=0,
                    text=top_prods["count"],
                    textposition="outside",
                    textfont=dict(color=TEXT_MUTED, size=10),
                ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=max(200, top_n_products * 32),
                    margin=dict(l=10, r=40, t=30, b=10),
                    title=dict(
                        text=f"<span style='color:{color}'>{seg}</span> · {engine}",
                        font=dict(size=11), x=0
                    ),
                    xaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
                               tickfont=dict(color=TEXT_MUTED, size=10),
                               title=dict(text="Times Recommended", font=dict(color=TEXT_MUTED, size=10))),
                    yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_PRIMARY, size=11)),
                )
                with col_widget:
                    st.markdown('<div class="chart-panel" style="margin-bottom:16px">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Segment profile summary cards ─────────────────────────────────────────────
st.markdown('<div class="section-header">Segment Profile Cards</div>', unsafe_allow_html=True)

card_cols = st.columns(min(len(view_segs), 3))
for i, (_, row) in enumerate(view_profile.iterrows()):
    seg   = row["customer_segment"]
    color = SEGMENT_COLORS.get(seg, DEFAULT_COLOR)
    col   = card_cols[i % len(card_cols)]
    with col:
        st.markdown(f"""
        <div class="seg-card">
          <div class="seg-card-name" style="color:{color}">{seg}</div>
          <div class="seg-stat-row">
            <span class="seg-stat-label">Customers</span>
            <span class="seg-stat-value">{int(row['customer_count']):,}</span>
          </div>
          <div class="seg-stat-row">
            <span class="seg-stat-label">Avg Age</span>
            <span class="seg-stat-value">{row['avg_age']:.0f}</span>
          </div>
          <div class="seg-stat-row">
            <span class="seg-stat-label">Avg Income</span>
            <span class="seg-stat-value">₹{row['avg_income']:,.0f}</span>
          </div>
          <div class="seg-stat-row">
            <span class="seg-stat-label">Avg Tenure</span>
            <span class="seg-stat-value">{row['avg_tenure']:.0f} mo</span>
          </div>
          <div class="seg-stat-row">
            <span class="seg-stat-label">Avg Engagement</span>
            <span class="seg-stat-value">{row['avg_engagement']:.2f}</span>
          </div>
          <div class="seg-stat-row">
            <span class="seg-stat-label">Avg Risk</span>
            <span class="seg-stat-value">{row['avg_risk']:.2f}</span>
          </div>
          <div class="seg-stat-row">
            <span class="seg-stat-label">Avg Products Owned</span>
            <span class="seg-stat-value">{row['avg_owned']:.1f}</span>
          </div>
          <div class="seg-stat-row">
            <span class="seg-stat-label">Avg FP Recs</span>
            <span class="seg-stat-value" style="color:{FP_COLOR}">{row['avg_fp_recs']:.1f}</span>
          </div>
          <div class="seg-stat-row">
            <span class="seg-stat-label">Avg IBCF Recs</span>
            <span class="seg-stat-value" style="color:{IBCF_COLOR}">{row['avg_ibcf_recs']:.1f}</span>
          </div>
        </div>""", unsafe_allow_html=True)