import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Diversity Analytics · RecoIQ",
    page_icon="🌐",
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

FP_COLOR       = "#39D0C8"
IBCF_COLOR     = "#7C5CFC"


SEGMENT_COLORS = {
    "Young Digital User": "#39D0C8",
    "Working Professional": "#7C5CFC",
    "Family Builder": "#F0A500",
    "Wealth Creator": "#3FB950",
    "Retirement Planner": "#F75D7E",
}


# ── Styling ──────────────────────────────────────────────────────────────────
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

[data-testid="stSidebar"] * {{
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

div[data-testid="stPlotlyChart"] {{
    background: transparent !important;
}}

</style>
""", unsafe_allow_html=True)


# ── Data Loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_overlap():
    return pd.read_csv(
        "data/recommendation_overlap_analysis.csv"
    )


@st.cache_data(ttl=300, show_spinner=False)
def load_all_recommendations():
    return pd.read_csv(
        "data/all_recommendations.csv"
    )


@st.cache_data(ttl=300, show_spinner=False)
def load_customer_360():
    return pd.read_csv(
        "data/customer_360_enhanced.csv"
    )


@st.cache_data(ttl=300, show_spinner=False)
def load_products():
    return pd.read_csv(
        "data/products.csv"
    )


# ── Load Data ─────────────────────────────────────────────────────────────────
with st.spinner("Loading diversity metrics..."):
    try:
        overlap_df = load_overlap()
        all_recs   = load_all_recommendations()
        c360       = load_customer_360()
        products   = load_products()

        load_ok = True

    except Exception as e:
        st.error(f"Data load failed: {e}")
        load_ok = False


if not load_ok:
    st.stop()


# ── Derived Metrics ───────────────────────────────────────────────────────────

avg_overlap = (
    overlap_df["overlap_ratio"].mean()
    if "overlap_ratio" in overlap_df.columns
    else 0
)

median_overlap = (
    overlap_df["overlap_ratio"].median()
    if "overlap_ratio" in overlap_df.columns
    else 0
)

pct_zero_overlap = (
    (overlap_df["overlap_ratio"] == 0).mean()
    if "overlap_ratio" in overlap_df.columns
    else 0
)

pct_high_overlap = (
    (overlap_df["overlap_ratio"] >= 0.5).mean()
    if "overlap_ratio" in overlap_df.columns
    else 0
)

unique_products = (
    all_recs["product_name"].nunique()
    if "product_name" in all_recs.columns
    else 0
)

catalog_size = (
    products["product_name"].nunique()
    if "product_name" in products.columns
    else unique_products
)

catalog_coverage = (
    unique_products / catalog_size
    if catalog_size > 0
    else 0
)

total_customers = len(c360)


# ── Engine Coverage Metrics ───────────────────────────────────────────────────

fp_unique_products = 0
ibcf_unique_products = 0

if (
    not all_recs.empty
    and "engine" in all_recs.columns
    and "product_name" in all_recs.columns
):

    fp_mask = all_recs["engine"].astype(str).str.contains(
        "FP",
        case=False,
        na=False
    )

    ibcf_mask = all_recs["engine"].astype(str).str.contains(
        "IBCF",
        case=False,
        na=False
    )

    fp_unique_products = (
        all_recs.loc[fp_mask, "product_name"]
        .nunique()
    )

    ibcf_unique_products = (
        all_recs.loc[ibcf_mask, "product_name"]
        .nunique()
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown(
        f"<div style='font-size:1.1rem;font-weight:800;color:{ACCENT_TEAL};margin-bottom:4px'>RecoIQ</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div style='font-size:0.7rem;color:{TEXT_MUTED};margin-bottom:24px'>Recommendation Intelligence Platform</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    top_n_products = st.slider(
        "Top Products",
        5,
        30,
        15
    )

    st.markdown("---")

    st.markdown(
        f"<div style='font-size:0.72rem;color:{TEXT_MUTED}'>Customers analysed</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div style='font-size:1.3rem;font-weight:800;color:{ACCENT_TEAL}'>{total_customers:,}</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div style='font-size:0.72rem;color:{TEXT_MUTED};margin-top:8px'>Catalog coverage</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div style='font-size:1.3rem;font-weight:800;color:{ACCENT_AMBER}'>{catalog_coverage:.1%}</div>",
        unsafe_allow_html=True
    )


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-eyebrow">Recommendation Diversity</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="page-title">Diversity Analytics</p>',
    unsafe_allow_html=True
)

st.markdown(
    f'<p class="page-subtitle">Recommendation overlap, catalog coverage, diversity metrics, and product discovery behaviour across {total_customers:,} customers</p>',
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)


# ── KPI Strip ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)


def kpi(col, value, label, color=ACCENT_TEAL, sub=None):

    sub_html = (
        f'<div class="kpi-sub">{sub}</div>'
        if sub else ""
    )

    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color:{color}">
                {value}
            </div>
            <div class="kpi-label">
                {label}
            </div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True
    )


kpi(
    k1,
    f"{avg_overlap:.1%}",
    "Average Overlap",
    ACCENT_AMBER
)

kpi(
    k2,
    f"{unique_products:,}",
    "Products Recommended",
    ACCENT_TEAL
)

kpi(
    k3,
    f"{catalog_coverage:.1%}",
    "Catalog Coverage",
    ACCENT_GREEN
)

kpi(
    k4,
    f"{pct_zero_overlap:.1%}",
    "Zero Overlap",
    ACCENT_ROSE
)

kpi(
    k5,
    f"{pct_high_overlap:.1%}",
    "High Overlap ≥ 50%",
    ACCENT_VIOLET
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Overlap Distribution ─────────────────────────────────────────────────────
st.markdown(
    '<div class="section-header">Recommendation Overlap Distribution</div>',
    unsafe_allow_html=True
)

left, right = st.columns([1.6, 1])

with left:

    if "overlap_ratio" in overlap_df.columns:

        fig_overlap = go.Figure(
            go.Histogram(
                x=overlap_df["overlap_ratio"],
                nbinsx=20,
                marker_color=ACCENT_AMBER,
                marker_line_color=DARK_BG,
                marker_line_width=1.5,
                opacity=0.9,
            )
        )

        fig_overlap.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            bargap=0.05,
            xaxis=dict(
                range=[0, 1],
                showgrid=False,
                zeroline=False,
                tickfont=dict(color=TEXT_MUTED),
                title=dict(
                    text="Recommendation Overlap Ratio",
                    font=dict(color=TEXT_MUTED)
                ),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=PANEL_BORDER,
                zeroline=False,
                tickfont=dict(color=TEXT_MUTED),
                title=dict(
                    text="Customers",
                    font=dict(color=TEXT_MUTED)
                ),
            ),
        )

        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        st.plotly_chart(
            fig_overlap,
            use_container_width=True,
            config={"displayModeBar": False}
        )
        st.markdown("</div>", unsafe_allow_html=True)


with right:

    stats = [
        (
            "Median Overlap",
            f"{median_overlap:.1%}",
            ACCENT_AMBER
        ),
        (
            "Zero Overlap",
            f"{pct_zero_overlap:.1%}",
            ACCENT_ROSE
        ),
        (
            "High Overlap",
            f"{pct_high_overlap:.1%}",
            ACCENT_VIOLET
        ),
        (
            "Catalog Coverage",
            f"{catalog_coverage:.1%}",
            ACCENT_GREEN
        ),
    ]

    for label, value, color in stats:

        st.markdown(
            f"""
            <div class="kpi-card" style="margin-bottom:10px">
                <div class="kpi-value"
                     style="font-size:1.5rem;color:{color}">
                     {value}
                </div>
                <div class="kpi-label">
                    {label}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


st.markdown("<br>", unsafe_allow_html=True)


# ── Engine Catalog Diversity ────────────────────────────────────────────────
st.markdown(
    '<div class="section-header">Catalog Coverage by Engine</div>',
    unsafe_allow_html=True
)

coverage_df = pd.DataFrame({
    "Engine": ["FP-Growth", "IBCF"],
    "Products": [
        fp_unique_products,
        ibcf_unique_products
    ]
})

fig_cov = go.Figure()

fig_cov.add_trace(
    go.Bar(
        x=coverage_df["Engine"],
        y=coverage_df["Products"],
        marker_color=[FP_COLOR, IBCF_COLOR],
        marker_line_width=0,
        text=coverage_df["Products"],
        textposition="outside",
        textfont=dict(
            color=TEXT_MUTED,
            size=11
        )
    )
)

fig_cov.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=300,
    margin=dict(l=10, r=10, t=10, b=10),
    showlegend=False,
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        tickfont=dict(color=TEXT_MUTED)
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=PANEL_BORDER,
        zeroline=False,
        tickfont=dict(color=TEXT_MUTED),
        title=dict(
            text="Unique Products Recommended",
            font=dict(color=TEXT_MUTED)
        )
    ),
)

st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
st.plotly_chart(
    fig_cov,
    use_container_width=True,
    config={"displayModeBar": False}
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Segment Diversity Analysis ───────────────────────────────────────────────
st.markdown(
    '<div class="section-header">Diversity by Customer Segment</div>',
    unsafe_allow_html=True
)

segment_diversity = pd.DataFrame()

if (
    not all_recs.empty
    and "product_name" in all_recs.columns
):

    rec_seg = all_recs.merge(
        c360[
            ["customer_id", "customer_segment"]
        ],
        on="customer_id",
        how="left"
    )

    segment_diversity = (
        rec_seg.groupby("customer_segment")
        .agg(
            unique_products=("product_name", "nunique"),
            recommendation_count=("product_name", "count")
        )
        .reset_index()
    )

if not segment_diversity.empty:

    fig_seg_div = go.Figure()

    fig_seg_div.add_trace(
        go.Bar(
            x=segment_diversity["customer_segment"],
            y=segment_diversity["unique_products"],
            marker_color=[
                SEGMENT_COLORS.get(
                    s,
                    ACCENT_TEAL
                )
                for s in segment_diversity["customer_segment"]
            ],
            marker_line_width=0,
            text=segment_diversity["unique_products"],
            textposition="outside",
            textfont=dict(
                color=TEXT_MUTED,
                size=10
            )
        )
    )

    fig_seg_div.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(color=TEXT_MUTED)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=PANEL_BORDER,
            zeroline=False,
            tickfont=dict(color=TEXT_MUTED),
            title=dict(
                text="Unique Products Recommended",
                font=dict(color=TEXT_MUTED)
            )
        ),
    )

    st.markdown(
        '<div class="chart-panel">',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        fig_seg_div,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# ── Product Discovery Ranking ────────────────────────────────────────────────
st.markdown(
    '<div class="section-header">Top Discovery Products</div>',
    unsafe_allow_html=True
)

discovery_df = (
    all_recs.groupby("product_name")
    .size()
    .reset_index(name="recommendation_count")
    .sort_values(
        "recommendation_count",
        ascending=False
    )
)

discovery_df = discovery_df.head(
    top_n_products
).sort_values(
    "recommendation_count",
    ascending=True
)

fig_disc = go.Figure(
    go.Bar(
        x=discovery_df["recommendation_count"],
        y=discovery_df["product_name"],
        orientation="h",
        marker_color=ACCENT_GREEN,
        marker_line_width=0,
        text=discovery_df["recommendation_count"],
        textposition="outside",
        textfont=dict(
            color=TEXT_MUTED,
            size=10
        )
    )
)

fig_disc.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=max(
        280,
        len(discovery_df) * 30
    ),
    margin=dict(
        l=10,
        r=50,
        t=10,
        b=10
    ),
    showlegend=False,
    xaxis=dict(
        showgrid=True,
        gridcolor=PANEL_BORDER,
        zeroline=False,
        tickfont=dict(color=TEXT_MUTED),
        title=dict(
            text="Recommendation Volume",
            font=dict(color=TEXT_MUTED)
        )
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        tickfont=dict(color=TEXT_PRIMARY)
    ),
)

st.markdown(
    '<div class="chart-panel">',
    unsafe_allow_html=True
)

st.plotly_chart(
    fig_disc,
    use_container_width=True,
    config={"displayModeBar": False}
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)
