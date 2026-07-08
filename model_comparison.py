import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Model Comparison · RecoIQ",
    page_icon="⚖️",
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
  .winner-badge {{
      display: inline-block;
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 3px 10px;
      border-radius: 20px;
      margin-top: 6px;
  }}
  .verdict-panel {{
      background: {PANEL_BG};
      border: 1px solid {PANEL_BORDER};
      border-radius: 10px;
      padding: 22px 26px;
  }}
  .verdict-title {{
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: {TEXT_MUTED};
      margin-bottom: 10px;
  }}
  .verdict-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 9px 0;
      border-bottom: 1px solid {PANEL_BORDER};
  }}
  .verdict-row:last-child {{ border-bottom: none; }}
  .verdict-metric {{ font-size: 0.82rem; color: {TEXT_MUTED}; }}
  .verdict-winner {{ font-size: 0.85rem; font-weight: 700; }}
  div[data-testid="stPlotlyChart"] {{ background: transparent !important; }}
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
def load_overlap():
    return pd.read_csv(
        "data/recommendation_overlap_analysis.csv"
    )

with st.spinner("Loading comparison data…"):
    try:
        eng_df   = load_engine_comparison()
        seg_fp   = load_segment_fp()
        seg_ibcf = load_segment_ibcf()
        prod_df  = load_product_comparison()
        overlap  = load_overlap()
        load_ok  = True
    except Exception as e:
        st.error(f"Data load failed: {e}")
        load_ok = False

if not load_ok:
    st.stop()

# ── Pull engine rows ──────────────────────────────────────────────────────────
fp_row   = eng_df[eng_df["engine"].str.contains("FP",   case=False, na=False)].iloc[0] if not eng_df.empty else None
ibcf_row = eng_df[eng_df["engine"].str.contains("IBCF", case=False, na=False)].iloc[0] if not eng_df.empty else None

def safe(row, key, default=0):
    try:
        return row[key] if row is not None else default
    except Exception:
        return default

fp_recs   = int(safe(fp_row,   "recommendation_count", 0))
ibcf_recs = int(safe(ibcf_row, "recommendation_count", 0))
fp_cov    = float(safe(fp_row,   "customer_coverage", 0))
ibcf_cov  = float(safe(ibcf_row, "customer_coverage", 0))
fp_cat    = float(safe(fp_row,   "catalog_coverage", 0))
ibcf_cat  = float(safe(ibcf_row, "catalog_coverage", 0))
fp_score  = float(safe(fp_row,   "average_score", 0))
ibcf_score= float(safe(ibcf_row, "average_score", 0))

avg_overlap = float(overlap["overlap_ratio"].mean()) if "overlap_ratio" in overlap.columns else 0

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='font-size:1.1rem;font-weight:800;color:{ACCENT_TEAL};margin-bottom:4px'>RecoIQ</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.7rem;color:{TEXT_MUTED};margin-bottom:24px'>Recommendation Intelligence Platform</div>", unsafe_allow_html=True)
    st.markdown("---")
    top_n = st.slider("Top Products (divergence chart)", 5, 25, 12)
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.72rem;color:{TEXT_MUTED}'>Avg recommendation overlap</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1.3rem;font-weight:800;color:{ACCENT_AMBER}'>{avg_overlap:.1%}</div>", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown('<div class="page-eyebrow">Engine Analysis</div>', unsafe_allow_html=True)
st.markdown('<p class="page-title">Model Comparison</p>', unsafe_allow_html=True)
st.markdown(f'<p class="page-subtitle">FP-Growth vs IBCF — coverage, scoring, product reach, and per-segment divergence</p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── KPI strip ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, value, label, color, sub=None):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-value" style="color:{color}">{value}</div>
      <div class="kpi-label">{label}</div>
      {sub_html}
    </div>""", unsafe_allow_html=True)

recs_winner  = "FP" if fp_recs   > ibcf_recs  else "IBCF"
cov_winner   = "FP" if fp_cov    > ibcf_cov   else "IBCF"
score_winner = "FP" if fp_score  > ibcf_score else "IBCF"

kpi(k1, f"{fp_recs:,}",    "FP-Growth Recs",      FP_COLOR,    f"vs {ibcf_recs:,} IBCF")
kpi(k2, f"{fp_cov:.1%}",   "FP Customer Coverage", FP_COLOR,    f"vs {ibcf_cov:.1%} IBCF")
kpi(k3, f"{fp_score:.4f}", "FP Avg Score",         FP_COLOR,    f"vs {ibcf_score:.4f} IBCF")
kpi(k4, f"{ibcf_cat:.1%}", "IBCF Catalog Coverage",IBCF_COLOR,  f"vs {fp_cat:.1%} FP")
kpi(k5, f"{avg_overlap:.1%}", "Avg Overlap Ratio", ACCENT_AMBER, "across all customers")

st.markdown("<br>", unsafe_allow_html=True)

# ── Head-to-head radar ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Head-to-Head · Multi-Axis Comparison</div>', unsafe_allow_html=True)

radar_l, radar_r = st.columns([1.2, 0.8])

with radar_l:
    categories   = ["Rec Volume", "Customer Coverage", "Catalog Coverage", "Avg Score"]
    # normalise each axis to 0–1 relative to the max between the two engines
    fp_raw   = [fp_recs,   fp_cov,   fp_cat,   fp_score]
    ibcf_raw = [ibcf_recs, ibcf_cov, ibcf_cat, ibcf_score]
    maxes    = [max(a, b) or 1 for a, b in zip(fp_raw, ibcf_raw)]
    fp_norm  = [a / m for a, m in zip(fp_raw,   maxes)]
    ib_norm  = [b / m for b, m in zip(ibcf_raw, maxes)]

    fig_radar = go.Figure()

    for vals, name, color in [
        (fp_norm, "FP-Growth", FP_COLOR),
        (ib_norm, "IBCF", IBCF_COLOR)
    ]:
        fill_color = (
            "rgba(57, 208, 200, 0.15)"
            if name == "FP-Growth"
            else "rgba(124, 92, 252, 0.15)"
        )

        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor=fill_color,
            line=dict(
                color=color,
                width=2.5
            ),
            name=name,
            hovertemplate="%{theta}: %{r:.2f}<extra>" + name + "</extra>",
        ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(color=TEXT_MUTED, size=9),
                            gridcolor=PANEL_BORDER, linecolor=PANEL_BORDER),
            angularaxis=dict(tickfont=dict(color=TEXT_PRIMARY, size=12), linecolor=PANEL_BORDER),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color=TEXT_PRIMARY), bgcolor="rgba(0,0,0,0)",
                    orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5),
        height=360,
        margin=dict(l=50, r=50, t=30, b=50),
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ── Verdict table ─────────────────────────────────────────────────────────────
with radar_r:
    def verdict(fp_val, ibcf_val, higher_is_better=True):
        if higher_is_better:
            if fp_val > ibcf_val:   return "FP-Growth", FP_COLOR
            elif ibcf_val > fp_val: return "IBCF",      IBCF_COLOR
            else:                   return "Tie",        ACCENT_AMBER
        else:
            if fp_val < ibcf_val:   return "FP-Growth", FP_COLOR
            elif ibcf_val < fp_val: return "IBCF",      IBCF_COLOR
            else:                   return "Tie",        ACCENT_AMBER

    metrics = [
        ("Recommendation Volume", fp_recs,    ibcf_recs,  True),
        ("Customer Coverage",     fp_cov,      ibcf_cov,   True),
        ("Catalog Coverage",      fp_cat,      ibcf_cat,   True),
        ("Average Score",         fp_score,    ibcf_score, True),
    ]

    rows_html = ""
    for label, fv, iv, hib in metrics:
        winner, color = verdict(fv, iv, hib)
        rows_html += f"""
        <div class="verdict-row">
          <span class="verdict-metric">{label}</span>
          <span class="verdict-winner" style="color:{color}">{winner}</span>
        </div>"""

    st.markdown(
        f"""
        <div class="verdict-panel">
            <div class="verdict-title">Metric Verdict</div>
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Per-segment divergence (grouped) ─────────────────────────────────────────
st.markdown('<div class="section-header">Per-Segment · Recommendation Volume Divergence</div>', unsafe_allow_html=True)

seg_fp_c   = seg_fp.copy().rename(columns={"recommendations_generated": "fp_recs",   "avg_score": "fp_score"})
seg_ibcf_c = seg_ibcf.copy().rename(columns={"recommendations_generated": "ibcf_recs", "avg_score": "ibcf_score"})
seg_merged = pd.merge(seg_fp_c, seg_ibcf_c, on="customer_segment", how="outer").fillna(0)
seg_merged["delta"] = seg_merged["fp_recs"] - seg_merged["ibcf_recs"]
seg_merged = seg_merged.sort_values("delta", ascending=True)

fig_div = go.Figure()
fig_div.add_trace(go.Bar(
    name="FP-Growth",
    x=seg_merged["customer_segment"],
    y=seg_merged["fp_recs"],
    marker_color=FP_COLOR,
    marker_line_width=0,
))
fig_div.add_trace(go.Bar(
    name="IBCF",
    x=seg_merged["customer_segment"],
    y=seg_merged["ibcf_recs"],
    marker_color=IBCF_COLOR,
    marker_line_width=0,
))
fig_div.update_layout(
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
st.plotly_chart(fig_div, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Per-segment avg score comparison ─────────────────────────────────────────
if "fp_score" in seg_merged.columns and "ibcf_score" in seg_merged.columns:
    st.markdown('<div class="section-header">Per-Segment · Average Score Comparison</div>', unsafe_allow_html=True)

    fig_score = go.Figure()
    seg_score = seg_merged.sort_values("fp_score", ascending=True)
    for col_name, color, label in [("fp_score", FP_COLOR, "FP-Growth"), ("ibcf_score", IBCF_COLOR, "IBCF")]:
        fig_score.add_trace(go.Bar(
            name=label,
            x=seg_score["customer_segment"],
            y=seg_score[col_name],
            marker_color=color,
            marker_line_width=0,
            text=seg_score[col_name].round(4),
            textposition="outside",
            textfont=dict(color=TEXT_MUTED, size=10),
        ))
    fig_score.update_layout(
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
    st.plotly_chart(fig_score, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# ── Product-level divergence (butterfly) ─────────────────────────────────────
st.markdown('<div class="section-header">Product-Level · Engine Divergence</div>', unsafe_allow_html=True)

if not prod_df.empty and "fp_count" in prod_df.columns and "ibcf_count" in prod_df.columns:
    prod_df["total"] = prod_df["fp_count"] + prod_df["ibcf_count"]
    top_prods = prod_df.sort_values("total", ascending=False).head(top_n).sort_values("fp_count", ascending=True)

    fig_butterfly = go.Figure()
    fig_butterfly.add_trace(go.Bar(
        name="FP-Growth",
        x=top_prods["fp_count"],
        y=top_prods["product_name"],
        orientation="h",
        marker_color=FP_COLOR,
        marker_line_width=0,
    ))
    fig_butterfly.add_trace(go.Bar(
        name="IBCF",
        x=[-v for v in top_prods["ibcf_count"]],
        y=top_prods["product_name"],
        orientation="h",
        marker_color=IBCF_COLOR,
        marker_line_width=0,
    ))

    max_val = max(top_prods["fp_count"].max(), top_prods["ibcf_count"].max())
    tick_vals = list(range(-int(max_val), int(max_val) + 1, max(1, int(max_val) // 5)))
    tick_text = [str(abs(v)) for v in tick_vals]

    fig_butterfly.update_layout(
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=max(320, top_n * 28),
        margin=dict(l=10, r=30, t=10, b=40),
        legend=dict(font=dict(color=TEXT_PRIMARY), bgcolor="rgba(0,0,0,0)",
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(
            showgrid=True, gridcolor=PANEL_BORDER, zeroline=True,
            zerolinecolor=TEXT_MUTED, zerolinewidth=1,
            tickfont=dict(color=TEXT_MUTED, size=10),
            tickvals=tick_vals, ticktext=tick_text,
            title=dict(text="← IBCF    FP-Growth →", font=dict(color=TEXT_MUTED, size=11)),
        ),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_PRIMARY, size=11)),
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_butterfly, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Overlap distribution ──────────────────────────────────────────────────────
st.markdown('<div class="section-header">Per-Customer · Recommendation Overlap Distribution</div>', unsafe_allow_html=True)

if "overlap_ratio" in overlap.columns:
    ol_l, ol_r = st.columns([1.5, 1])
    with ol_l:
        fig_ol = go.Figure(go.Histogram(
            x=overlap["overlap_ratio"],
            nbinsx=20,
            marker_color=ACCENT_AMBER,
            marker_line_color=DARK_BG,
            marker_line_width=1.5,
            opacity=0.85,
        ))
        fig_ol.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=260,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_MUTED),
                       title=dict(text="Overlap Ratio", font=dict(color=TEXT_MUTED, size=11)),
                       range=[0, 1]),
            yaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
                       tickfont=dict(color=TEXT_MUTED),
                       title=dict(text="Customers", font=dict(color=TEXT_MUTED, size=11))),
            bargap=0.06,
        )
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        st.plotly_chart(fig_ol, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with ol_r:
        pct_high = (overlap["overlap_ratio"] >= 0.5).mean()
        pct_none = (overlap["overlap_ratio"] == 0).mean()
        pct_full = (overlap["overlap_ratio"] == 1.0).mean()
        med_ol   = overlap["overlap_ratio"].median()

        stats = [
            ("Median Overlap",      f"{med_ol:.1%}",    ACCENT_AMBER),
            ("High Overlap (≥50%)", f"{pct_high:.1%}",  ACCENT_TEAL),
            ("Zero Overlap",        f"{pct_none:.1%}",  ACCENT_ROSE),
            ("Full Overlap (100%)", f"{pct_full:.1%}",  ACCENT_VIOLET),
        ]
        for label, val, color in stats:
            st.markdown(f"""
            <div class="kpi-card" style="margin-bottom:10px">
              <div class="kpi-value" style="color:{color};font-size:1.5rem">{val}</div>
              <div class="kpi-label">{label}</div>
            </div>""", unsafe_allow_html=True)