import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Executive Dashboard · RecoIQ",
    page_icon="🏆",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# Design System
# ─────────────────────────────────────────────────────────────

DARK_BG      = "#0D1117"
PANEL_BG     = "#161B22"
PANEL_BORDER = "#21262D"

ACCENT_TEAL   = "#39D0C8"
ACCENT_VIOLET = "#7C5CFC"
ACCENT_AMBER  = "#F0A500"
ACCENT_ROSE   = "#F75D7E"

TEXT_PRIMARY = "#E6EDF3"
TEXT_MUTED   = "#8B949E"

FP_COLOR   = "#39D0C8"
IBCF_COLOR = "#7C5CFC"

# Global page background only — no class-based rules
st.markdown(f"""
<style>
html, body, [data-testid="stAppViewContainer"] {{
    background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
}}
[data-testid="stSidebar"] {{
    background-color: {PANEL_BG};
    border-right: 1px solid {PANEL_BORDER};
}}
[data-testid="stSidebar"] * {{
    color: {TEXT_PRIMARY} !important;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Inline-style helpers
# ─────────────────────────────────────────────────────────────

def _card(content_html: str, extra_style: str = "") -> str:
    return (
        f'<div style="background:{PANEL_BG};border:1px solid {PANEL_BORDER};'
        f'border-radius:12px;padding:18px;{extra_style}">'
        f'{content_html}</div>'
    )

def _label(text: str) -> str:
    return (
        f'<div style="font-size:0.72rem;color:{TEXT_MUTED};'
        f'text-transform:uppercase;letter-spacing:0.08em;">{text}</div>'
    )

def _value(text: str, color: str, size: str = "2rem") -> str:
    return (
        f'<div style="font-size:{size};font-weight:800;color:{color};">{text}</div>'
    )

def _section_header(text: str) -> str:
    return (
        f'<div style="font-size:0.75rem;color:{TEXT_MUTED};letter-spacing:0.12em;'
        f'text-transform:uppercase;border-bottom:1px solid {PANEL_BORDER};'
        f'padding-bottom:8px;margin-bottom:16px;">{text}</div>'
    )

def kpi(col, value: str, label: str, color: str):
    col.markdown(
        _card(_value(value, color) + _label(label)),
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────────────────────
# Data Loaders
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_engine_comparison():
    return pd.read_csv("data/recommendation_engine_comparison.csv")

@st.cache_data(ttl=300)
def load_segment_fp():
    return pd.read_csv("data/segment_performance_fp.csv")

@st.cache_data(ttl=300)
def load_segment_ibcf():
    return pd.read_csv("data/segment_performance_ibcf.csv")

@st.cache_data(ttl=300)
def load_product_comparison():
    return pd.read_csv("data/product_recommendation_comparison.csv")

@st.cache_data(ttl=300)
def load_diversity():
    return pd.read_csv("data/diversity_summary.csv")

@st.cache_data(ttl=300)
def load_customer360():
    df = pd.read_csv("data/customer_360_enhanced.csv")
    for col in ["owned_products", "fp_recommendations", "ibcf_recommendations"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: (
                    [item.strip() for item in str(x).split(",")]
                    if pd.notna(x) and str(x).strip()
                    else []
                )
            )
    return df

@st.cache_data(ttl=300)
def load_recommendations():
    return pd.read_csv("data/all_recommendations.csv")

@st.cache_data(ttl=300)
def load_overlap():
    return pd.read_csv("data/recommendation_overlap_analysis.csv")

# ─────────────────────────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────────────────────────

with st.spinner("Loading executive intelligence..."):
    eng_df      = load_engine_comparison()
    seg_fp      = load_segment_fp()
    seg_ibcf    = load_segment_ibcf()
    prod_df     = load_product_comparison()
    diversity_df = load_diversity()
    c360        = load_customer360()
    recs_df     = load_recommendations()
    overlap_df  = load_overlap()

# ─────────────────────────────────────────────────────────────
# Core Metrics
# ─────────────────────────────────────────────────────────────

total_customers       = c360["customer_id"].nunique()
total_recommendations = len(recs_df)
total_products        = recs_df["product_name"].nunique()

customer_coverage = round(
    recs_df["customer_id"].nunique() / total_customers * 100, 2
)

fp_row = eng_df[eng_df["engine"].str.contains("FP", case=False, na=False)].iloc[0]
ibcf_row = eng_df[eng_df["engine"].str.contains("IBCF", case=False, na=False)].iloc[0]

fp_catalog   = fp_row["catalog_coverage"]   * 100
ibcf_catalog = ibcf_row["catalog_coverage"] * 100
catalog_coverage = round(max(fp_catalog, ibcf_catalog), 2)

avg_overlap = overlap_df["overlap_ratio"].mean() * 100
avg_score   = eng_df["average_score"].fillna(0).mean()

# ─────────────────────────────────────────────────────────────
# RecoIQ Score
# ─────────────────────────────────────────────────────────────

coverage_score  = min(customer_coverage, 100)
diversity_score = min(catalog_coverage,  100)
overlap_score   = min(avg_overlap,       100)
quality_score   = min(avg_score * 100,   100)

recoiq_score = round(
    (coverage_score + diversity_score + overlap_score + quality_score) / 4, 1
)

# ─────────────────────────────────────────────────────────────
# Platform Rating & Score Color
# ─────────────────────────────────────────────────────────────

if recoiq_score >= 85:
    platform_rating = "Excellent"
    score_color     = ACCENT_TEAL
elif recoiq_score >= 70:
    platform_rating = "Strong"
    score_color     = ACCENT_VIOLET
elif recoiq_score >= 55:
    platform_rating = "Moderate"
    score_color     = ACCENT_AMBER
else:
    platform_rating = "Needs Improvement"
    score_color     = ACCENT_ROSE

# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        f'<div style="font-size:1.2rem;font-weight:800;color:{ACCENT_TEAL};">RecoIQ</div>',
        unsafe_allow_html=True
    )
    st.markdown("Recommendation Intelligence Platform")
    st.markdown("---")
    st.metric("RecoIQ Score", f"{recoiq_score}/100")

# ─────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────

st.markdown(
    f'<div style="font-size:0.68rem;letter-spacing:0.14em;text-transform:uppercase;'
    f'font-weight:700;color:{ACCENT_TEAL};">Executive Intelligence</div>',
    unsafe_allow_html=True
)
st.markdown(
    f'<div style="font-size:2rem;font-weight:800;color:{TEXT_PRIMARY};">Executive Dashboard</div>',
    unsafe_allow_html=True
)
st.markdown(
    f'<div style="color:{TEXT_MUTED};font-size:0.9rem;">Strategic summary across recommendation '
    f'engines, segments, products and customer intelligence.</div>',
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Platform Health
# ─────────────────────────────────────────────────────────────

st.markdown(_section_header("Platform Health"), unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

kpi(c1, f"{total_customers:,}",        "Customers",         ACCENT_TEAL)
kpi(c2, f"{total_recommendations:,}",  "Recommendations",   ACCENT_VIOLET)
kpi(c3, f"{total_products}",           "Products",          ACCENT_AMBER)
kpi(c4, f"{customer_coverage:.1f}%",   "Customer Coverage", FP_COLOR)
kpi(c5, f"{catalog_coverage:.1f}%",    "Catalog Coverage",  IBCF_COLOR)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# RecoIQ Intelligence Score
# ─────────────────────────────────────────────────────────────

st.markdown(_section_header("RecoIQ Intelligence Score"), unsafe_allow_html=True)

score_left, score_right = st.columns([1, 2])

with score_left:
    st.markdown(
        f'<div style="background:linear-gradient(135deg,{ACCENT_TEAL}20,{ACCENT_VIOLET}20);'
        f'border:1px solid {PANEL_BORDER};border-radius:14px;padding:28px;text-align:center;">'
        f'<div style="font-size:3rem;font-weight:900;color:{TEXT_PRIMARY};">{recoiq_score}</div>'
        f'<div style="color:{TEXT_MUTED};text-transform:uppercase;letter-spacing:0.12em;">RecoIQ Score</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with score_right:
    score_df = pd.DataFrame({
        "Metric": ["Coverage", "Diversity", "Overlap", "Quality"],
        "Score":  [coverage_score, diversity_score, overlap_score, quality_score]
    })
    fig_score = go.Figure()
    fig_score.add_trace(go.Bar(
        x=score_df["Metric"],
        y=score_df["Score"],
        marker_color=[ACCENT_TEAL, ACCENT_VIOLET, ACCENT_AMBER, ACCENT_ROSE]
    ))
    fig_score.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=280, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(tickfont=dict(color=TEXT_PRIMARY)),
        yaxis=dict(range=[0, 100], tickfont=dict(color=TEXT_MUTED), gridcolor=PANEL_BORDER)
    )
    st.plotly_chart(fig_score, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Engine Intelligence Summary
# ─────────────────────────────────────────────────────────────

st.markdown(_section_header("Engine Intelligence Summary"), unsafe_allow_html=True)

def determine_winner(fp_val, ibcf_val):
    if fp_val > ibcf_val:
        return "FP-Growth"
    elif ibcf_val > fp_val:
        return "IBCF"
    return "Tie"

volume_winner   = determine_winner(fp_row["recommendation_count"], ibcf_row["recommendation_count"])
coverage_winner = determine_winner(fp_row["customer_coverage"],    ibcf_row["customer_coverage"])
catalog_winner  = determine_winner(fp_row["catalog_coverage"],     ibcf_row["catalog_coverage"])
score_winner    = determine_winner(fp_row["average_score"],        ibcf_row["average_score"])

w1, w2, w3, w4 = st.columns(4)

kpi(w1, volume_winner,   "Volume Leader",   FP_COLOR if volume_winner   == "FP-Growth" else IBCF_COLOR)
kpi(w2, coverage_winner, "Coverage Leader", FP_COLOR if coverage_winner == "FP-Growth" else IBCF_COLOR)
kpi(w3, catalog_winner,  "Catalog Leader",  FP_COLOR if catalog_winner  == "FP-Growth" else IBCF_COLOR)
kpi(w4, score_winner,    "Score Leader",    FP_COLOR if score_winner    == "FP-Growth" else IBCF_COLOR)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Executive Verdict
# ─────────────────────────────────────────────────────────────

st.success(f"🏆 Overall Platform Rating: {platform_rating}")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Segment Intelligence
# ─────────────────────────────────────────────────────────────

st.markdown(_section_header("Segment Intelligence"), unsafe_allow_html=True)

seg_fp_copy   = seg_fp.copy()
seg_ibcf_copy = seg_ibcf.copy()

seg_fp_copy.rename(
    columns={"recommendations_generated": "fp_recs", "avg_score": "fp_score"},
    inplace=True
)
seg_ibcf_copy.rename(
    columns={"recommendations_generated": "ibcf_recs", "avg_score": "ibcf_score"},
    inplace=True
)

segment_summary = pd.merge(
    seg_fp_copy, seg_ibcf_copy, on="customer_segment", how="outer"
).fillna(0)

segment_summary["total_recs"]       = segment_summary["fp_recs"]   + segment_summary["ibcf_recs"]
segment_summary["avg_engine_score"] = (segment_summary["fp_score"] + segment_summary["ibcf_score"]) / 2

top_segment = (
    segment_summary.sort_values("total_recs", ascending=False).iloc[0]
)
highest_score_segment = (
    segment_summary.sort_values("avg_engine_score", ascending=False).iloc[0]
)

s1, s2 = st.columns([1, 2])

with s1:
    st.markdown(
        _card(
            _label("Top Recommendation Segment")
            + _value(top_segment["customer_segment"], ACCENT_TEAL)
        ),
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        _card(
            _label("Highest Scoring Segment")
            + _value(highest_score_segment["customer_segment"], ACCENT_VIOLET)
        ),
        unsafe_allow_html=True
    )

with s2:
    chart_data = segment_summary.sort_values("total_recs", ascending=False)
    fig_seg = go.Figure()
    fig_seg.add_trace(go.Bar(
        x=chart_data["customer_segment"],
        y=chart_data["total_recs"],
        marker_color=ACCENT_TEAL
    ))
    fig_seg.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(tickfont=dict(color=TEXT_PRIMARY)),
        yaxis=dict(tickfont=dict(color=TEXT_MUTED), gridcolor=PANEL_BORDER)
    )
    st.plotly_chart(fig_seg, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Product Intelligence
# ─────────────────────────────────────────────────────────────

st.markdown(_section_header("Product Intelligence"), unsafe_allow_html=True)

prod_df["total"] = prod_df["fp_count"] + prod_df["ibcf_count"]
top_product = prod_df.sort_values("total", ascending=False).iloc[0]

p1, p2 = st.columns([1, 2])

with p1:
    st.markdown(
        _card(
            _label("Most Recommended Product")
            + _value(top_product["product_name"], ACCENT_AMBER, size="1.5rem")
            + "<br>"
            + _label(f"FP Recommendations: {int(top_product['fp_count'])}")
            + _label(f"IBCF Recommendations: {int(top_product['ibcf_count'])}")
        ),
        unsafe_allow_html=True
    )

with p2:
    chart_products = (
        prod_df.sort_values("total", ascending=False)
        .head(10)
        .sort_values("total", ascending=True)
    )
    fig_prod = go.Figure()
    fig_prod.add_trace(go.Bar(
        y=chart_products["product_name"], x=chart_products["fp_count"],
        orientation="h", name="FP-Growth", marker_color=FP_COLOR
    ))
    fig_prod.add_trace(go.Bar(
        y=chart_products["product_name"], x=chart_products["ibcf_count"],
        orientation="h", name="IBCF", marker_color=IBCF_COLOR
    ))
    fig_prod.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=380, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(gridcolor=PANEL_BORDER, tickfont=dict(color=TEXT_MUTED)),
        yaxis=dict(tickfont=dict(color=TEXT_PRIMARY))
    )
    st.plotly_chart(fig_prod, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Diversity Intelligence
# ─────────────────────────────────────────────────────────────

st.markdown(_section_header("Diversity Intelligence"), unsafe_allow_html=True)

d1, d2 = st.columns([1, 2])

with d1:
    for _, row in diversity_df.iterrows():
        engine_name     = row["engine"]
        unique_products = row["unique_products_recommended"]
        color = FP_COLOR if "FP" in engine_name.upper() else IBCF_COLOR
        st.markdown(
            _card(
                _label(engine_name)
                + _value(str(int(unique_products)), color)
                + _label("Unique Products Recommended"),
                extra_style="margin-bottom:10px;"
            ),
            unsafe_allow_html=True
        )

with d2:
    fig_diversity = go.Figure()
    fig_diversity.add_trace(go.Bar(
        x=diversity_df["engine"],
        y=diversity_df["unique_products_recommended"],
        marker_color=[FP_COLOR, IBCF_COLOR]
    ))
    fig_diversity.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(tickfont=dict(color=TEXT_PRIMARY)),
        yaxis=dict(gridcolor=PANEL_BORDER, tickfont=dict(color=TEXT_MUTED))
    )
    st.plotly_chart(fig_diversity, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Customer360 Highlights
# ─────────────────────────────────────────────────────────────

st.markdown(_section_header("Customer360 Highlights"), unsafe_allow_html=True)

customer_metrics = c360.copy()

def safe_len(x):
    if isinstance(x, list):
        return len(x)
    if pd.isna(x):
        return 0
    try:
        return len(str(x).split(","))
    except:
        return 0

customer_metrics["fp_rec_count"]   = customer_metrics["fp_recommendations"].apply(safe_len)
customer_metrics["ibcf_rec_count"] = customer_metrics["ibcf_recommendations"].apply(safe_len)
customer_metrics["total_rec_count"] = (
    customer_metrics["fp_rec_count"] + customer_metrics["ibcf_rec_count"]
)

highest_income_customer        = customer_metrics.sort_values("annual_income",    ascending=False).iloc[0]
highest_engagement_customer    = customer_metrics.sort_values("engagement_score", ascending=False).iloc[0]
highest_recommendation_customer = customer_metrics.sort_values("total_rec_count", ascending=False).iloc[0]

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        _card(
            _label("Highest Income Customer")
            + _value(highest_income_customer["customer_name"], ACCENT_TEAL, size="1.2rem")
            + _label(f"₹ {highest_income_customer['annual_income']:,.0f}")
        ),
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        _card(
            _label("Highest Engagement")
            + _value(highest_engagement_customer["customer_name"], ACCENT_VIOLET, size="1.2rem")
            + _label(f"Score: {highest_engagement_customer['engagement_score']:.2f}")
        ),
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        _card(
            _label("Most Recommended Customer")
            + _value(highest_recommendation_customer["customer_name"], ACCENT_AMBER, size="1.2rem")
            + _label(f"{highest_recommendation_customer['total_rec_count']} recommendations")
        ),
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Executive Narrative
# ─────────────────────────────────────────────────────────────

st.markdown(_section_header("Executive Narrative"), unsafe_allow_html=True)

top_product_name = top_product["product_name"]
top_segment_name = top_segment["customer_segment"]

if coverage_winner == "Tie":
    coverage_statement = "both engines demonstrate equal customer reach"
else:
    coverage_statement = f"{coverage_winner} demonstrates stronger customer reach"

executive_summary = (
    f"RecoIQ currently serves {total_customers:,} customers and has generated "
    f"{total_recommendations:,} recommendations across FP-Growth and "
    f"Item-Based Collaborative Filtering engines. "
    f"{volume_winner} currently leads recommendation volume generation, "
    f"while {coverage_statement}. "
    f"Catalog diversity is led by {catalog_winner}, ensuring broader product "
    f"discovery across the recommendation ecosystem. "
    f"The highest-performing customer segment is '{top_segment_name}', "
    f"generating the largest recommendation volume. "
    f"'{top_product_name}' remains the most recommended product across all "
    f"recommendation engines. "
    f"Current customer coverage stands at {customer_coverage:.1f}% with catalog "
    f"coverage of {catalog_coverage:.1f}%. "
    f"The overall RecoIQ Intelligence Score is {recoiq_score}/100, "
    f"resulting in a platform rating of '{platform_rating}'."
)

st.markdown(
    _card(
        f'<div style="color:{TEXT_PRIMARY};font-size:0.95rem;line-height:1.8;">'
        f'{executive_summary}</div>'
    ),
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Strategic Recommendations
# ─────────────────────────────────────────────────────────────

st.markdown(_section_header("Strategic Recommendations"), unsafe_allow_html=True)

recommendations = []

if customer_coverage < 80:
    recommendations.append(
        "Increase customer coverage by expanding recommendation eligibility rules."
    )
if catalog_coverage < 70:
    recommendations.append(
        "Improve catalog coverage through recommendation diversification strategies."
    )
if avg_overlap < 20:
    recommendations.append(
        "Low overlap indicates engine diversity. Evaluate recommendation consistency."
    )
if avg_overlap > 70:
    recommendations.append(
        "High overlap indicates redundancy. Increase recommendation diversity."
    )
if recoiq_score >= 85:
    recommendations.append(
        "Platform performance is strong. Focus on scaling and deployment readiness."
    )
if len(recommendations) == 0:
    recommendations.append(
        "Platform metrics appear balanced. Continue monitoring recommendation quality."
    )

for idx, rec in enumerate(recommendations, start=1):
    st.markdown(
        _card(
            f'<span style="color:{TEXT_PRIMARY};font-size:0.95rem;">'
            f'<b>{idx}.</b> {rec}</span>',
            extra_style="margin-bottom:10px;"
        ),
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CEO Summary Panel
# ─────────────────────────────────────────────────────────────

st.markdown(
    f'<div style="background:linear-gradient(135deg,{ACCENT_TEAL}20,{ACCENT_VIOLET}20);'
    f'border:1px solid {PANEL_BORDER};border-radius:14px;padding:28px;text-align:center;">'
    f'<div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.15em;'
    f'color:{TEXT_MUTED};margin-bottom:12px;">RecoIQ Executive Assessment</div>'
    f'<div style="font-size:3rem;font-weight:900;color:{score_color};">{recoiq_score}/100</div>'
    f'<div style="margin-top:10px;font-size:1rem;color:{TEXT_PRIMARY};font-weight:700;">'
    f'{platform_rating}</div>'
    f'<div style="margin-top:12px;color:{TEXT_MUTED};">'
    f'Recommendation Intelligence Platform Health Rating</div>'
    f'</div>',
    unsafe_allow_html=True
)