import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go


# ─────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Customer 360 · RecoIQ",
    page_icon="👤",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# Theme
# ─────────────────────────────────────────────────────────────

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

# ─────────────────────────────────────────────────────────────
# Styling
# ─────────────────────────────────────────────────────────────

st.markdown(
f"""
<style>

html, body, [data-testid="stAppViewContainer"] {{
    background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
}}

[data-testid="stSidebar"] {{
    background-color: {PANEL_BG};
    border-right:1px solid {PANEL_BORDER};
}}

[data-testid="stSidebar"] * {{
    color:{TEXT_PRIMARY} !important;
}}

.page-eyebrow {{
    font-size:0.68rem;
    font-weight:600;
    letter-spacing:0.14em;
    text-transform:uppercase;
    color:{ACCENT_TEAL};
}}

.page-title {{
    font-size:1.9rem;
    font-weight:800;
}}

.page-subtitle {{
    color:{TEXT_MUTED};
    font-size:0.85rem;
}}

.section-header {{
    font-size:0.72rem;
    text-transform:uppercase;
    color:{TEXT_MUTED};
    border-bottom:1px solid {PANEL_BORDER};
    padding-bottom:6px;
    margin-bottom:16px;
    letter-spacing:0.12em;
}}

.kpi-card {{
    background:{PANEL_BG};
    border:1px solid {PANEL_BORDER};
    border-radius:10px;
    padding:18px 22px;
}}

.kpi-value {{
    font-size:1.9rem;
    font-weight:800;
}}

.kpi-label {{
    font-size:0.72rem;
    color:{TEXT_MUTED};
    text-transform:uppercase;
}}

.chart-panel {{
    background:{PANEL_BG};
    border:1px solid {PANEL_BORDER};
    border-radius:10px;
    padding:20px;
}}

.chip {{
    display:inline-block;
    padding:6px 12px;
    margin:4px;
    border-radius:6px;
    background:{PANEL_BG};
    border:1px solid {PANEL_BORDER};
    font-size:0.78rem;
}}

</style>
""",
unsafe_allow_html=True
)


# ─────────────────────────────────────────────────────────────
# Data Loading
# ─────────────────────────────────────────────────────────────

@st.cache_data
def load_customer360():
    return pd.read_csv(
        "data/customer_360_enhanced.csv"
    )


@st.cache_data
def load_all_recommendations():
    return pd.read_csv(
        "data/all_recommendations.csv"
    )


@st.cache_data
def load_overlap():
    return pd.read_csv(
        "data/recommendation_overlap_analysis.csv"
    )

@st.cache_data
def load_products():
    return pd.read_csv(
        "data/products.csv"
    )

# ─────────────────────────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────────────────────────
def parse_overlap_products(x):
    """
    Converts:
    ['P001' 'P018' 'P017']

    into:
    ['P001', 'P018', 'P017']
    """
    
    if pd.isna(x):
        return []

    if isinstance(x, list):
        return x

    return re.findall(r"P\d+", str(x))

with st.spinner("Loading customer intelligence..."):

    c360 = load_customer360()
    all_recs = load_all_recommendations()
    overlap_df = load_overlap()
    products_df = load_products()

    # Convert overlap product IDs from CSV strings into lists
    for col in [
        "fp_products",
        "ibcf_products"
    ]:
        if col in overlap_df.columns:
            overlap_df[col] = overlap_df[col].apply(
                parse_overlap_products
            )

    # Product ID → Product Name mapping
    product_map = dict(
        zip(
            products_df["product_id"],
            products_df["product_name"]
        )
    )

# ─────────────────────────────────────────────────────────────
# Parse String Lists
# ─────────────────────────────────────────────────────────────

def parse_list(x):

    if isinstance(x, list):
        return x

    if pd.isna(x):
        return []

    return [
        item.strip()
        for item in str(x).split(",")
        if item.strip()
    ]

for col in [
    "owned_products",
    "fp_recommendations",
    "ibcf_recommendations"
]:

    c360[col] = c360[col].apply(parse_list)

# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────

with st.sidebar:

    st.markdown(
        f"<div style='font-size:1.1rem;font-weight:800;color:{ACCENT_TEAL}'>RecoIQ</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div style='font-size:0.72rem;color:{TEXT_MUTED};margin-bottom:20px'>Recommendation Intelligence Platform</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    selected_customer = st.selectbox(
        "Select Customer",
        sorted(c360["customer_id"].unique())
    )

# ─────────────────────────────────────────────────────────────
# Selected Customer
# ─────────────────────────────────────────────────────────────

cust = c360[
    c360["customer_id"] == selected_customer
].iloc[0]

cust_recs = all_recs[
    all_recs["customer_id"] == selected_customer
]

fp_recs = cust_recs[
    cust_recs["engine"].str.contains(
        "FP",
        case=False,
        na=False
    )
]

ibcf_recs = cust_recs[
    cust_recs["engine"].str.contains(
        "IBCF",
        case=False,
        na=False
    )
]

# ─────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="page-eyebrow">Customer Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="page-title">Customer 360 Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="page-subtitle">
    {cust["customer_name"]} · {cust["customer_segment"]}
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Customer Profile KPIs
# ─────────────────────────────────────────────────────────────

c1,c2,c3,c4,c5,c6 = st.columns(6)

metrics = [

    ("Age",
     int(cust["age"]),
     ACCENT_TEAL),

    ("Income",
     f"₹{cust['annual_income']:,.0f}",
     ACCENT_VIOLET),

    ("City",
     cust["city"],
     ACCENT_AMBER),

    ("Tenure",
     f"{cust['tenure_months']} mo",
     ACCENT_GREEN),

    ("Engagement",
     cust["engagement_score"],
     FP_COLOR),

    ("Risk",
     cust["risk_score"],
     ACCENT_ROSE)
]

for col, metric in zip(
    [c1,c2,c3,c4,c5,c6],
    metrics
):

    label,value,color = metric

    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color:{color}">
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

# ─────────────────────────────────────────────────────────────
# Portfolio KPIs
# ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="section-header">Portfolio Overview</div>',
    unsafe_allow_html=True
)

k1,k2,k3,k4 = st.columns(4)

portfolio_metrics = [

    (
        "Owned Products",
        len(cust["owned_products"]),
        ACCENT_TEAL
    ),

    (
        "FP Recommendations",
        len(fp_recs),
        FP_COLOR
    ),

    (
        "IBCF Recommendations",
        len(ibcf_recs),
        IBCF_COLOR
    ),

    (
        "Total Recommendations",
        len(cust_recs),
        ACCENT_AMBER
    )
]

for col, metric in zip(
    [k1,k2,k3,k4],
    portfolio_metrics
):

    label,value,color = metric

    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color:{color}">
                {value}
            </div>
            <div class="kpi-label">
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────────────────────
# Owned Products
# ─────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-header">Owned Products</div>',
    unsafe_allow_html=True
)

chips_html = ""

for p in cust["owned_products"]:

    chips_html += f"""
    <span class="chip">
        {p}
    </span>
    """

st.markdown(
    chips_html,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Recommendation Comparison
# ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="section-header">Recommendation Comparison</div>',
    unsafe_allow_html=True
)

left_col, right_col = st.columns(2)

# ------------------------------------------------------------
# FP Recommendations
# ------------------------------------------------------------

with left_col:

    st.markdown(
        f"""
        <div class="kpi-card">
            <h4 style="color:{FP_COLOR};margin-top:0">
                FP-Growth Recommendations
            </h4>
        """,
        unsafe_allow_html=True
    )

    if not fp_recs.empty:

        fp_display = fp_recs[
            [
                "rank",
                "product_name",
                "recommendation_score"
            ]
        ].sort_values("rank")

        st.dataframe(
            fp_display,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No FP recommendations available.")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# IBCF Recommendations
# ------------------------------------------------------------

with right_col:

    st.markdown(
        f"""
        <div class="kpi-card">
            <h4 style="color:{IBCF_COLOR};margin-top:0">
                IBCF Recommendations
            </h4>
        """,
        unsafe_allow_html=True
    )

    if not ibcf_recs.empty:

        ibcf_display = ibcf_recs[
            [
                "rank",
                "product_name",
                "recommendation_score"
            ]
        ].sort_values("rank")

        st.dataframe(
            ibcf_display,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No IBCF recommendations available.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Recommendation Strength Comparison
# ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="section-header">Recommendation Strength Comparison</div>',
    unsafe_allow_html=True
)

comparison_df = pd.DataFrame()

if not fp_recs.empty or not ibcf_recs.empty:

    fp_tmp = fp_recs[
        ["product_name", "recommendation_score"]
    ].rename(
        columns={
            "recommendation_score": "fp_score"
        }
    )

    ibcf_tmp = ibcf_recs[
        ["product_name", "recommendation_score"]
    ].rename(
        columns={
            "recommendation_score": "ibcf_score"
        }
    )

    comparison_df = fp_tmp.merge(
        ibcf_tmp,
        on="product_name",
        how="outer"
    ).fillna(0)

if not comparison_df.empty:

    fig_scores = go.Figure()

    fig_scores.add_trace(
        go.Bar(
            name="FP-Growth",
            x=comparison_df["product_name"],
            y=comparison_df["fp_score"],
            marker_color=FP_COLOR
        )
    )

    fig_scores.add_trace(
        go.Bar(
            name="IBCF",
            x=comparison_df["product_name"],
            y=comparison_df["ibcf_score"],
            marker_color=IBCF_COLOR
        )
    )

    fig_scores.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=420,
        legend=dict(
            orientation="h",
            y=1.05,
            font=dict(color=TEXT_PRIMARY)
        ),
        xaxis=dict(
            tickfont=dict(color=TEXT_MUTED)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=PANEL_BORDER,
            tickfont=dict(color=TEXT_MUTED)
        )
    )

    st.markdown(
        '<div class="chart-panel">',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        fig_scores,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Explainability
# ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="section-header">Recommendation Explainability</div>',
    unsafe_allow_html=True
)

exp_left, exp_right = st.columns(2)

# ------------------------------------------------------------
# FP Explainability
# ------------------------------------------------------------

with exp_left:

    st.markdown(
        f"""
        <div class="kpi-card">
        <h4 style="color:{FP_COLOR};margin-top:0">
        FP-Growth Reasoning
        </h4>
        """,
        unsafe_allow_html=True
    )

    if not fp_recs.empty:

        selected_fp_product = st.selectbox(
            "FP Recommendation",
            fp_recs["product_name"].tolist(),
            key="fp_explain"
        )

        fp_row = fp_recs[
            fp_recs["product_name"]
            == selected_fp_product
        ].iloc[0]

        confidence = fp_row.get("confidence", 0)
        lift = fp_row.get("lift", 0)
        support = fp_row.get("support", 0)

        st.metric(
            "Confidence",
            f"{confidence:.2%}"
        )

        st.metric(
            "Lift",
            f"{lift:.2f}"
        )

        st.metric(
            "Support",
            f"{support:.2%}"
        )

        st.markdown("#### Explanation")

        st.write(
            fp_row.get("reason", "")
        )

    else:

        st.info("No FP explanations available.")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# IBCF Explainability
# ------------------------------------------------------------

with exp_right:

    st.markdown(
        f"""
        <div class="kpi-card">
        <h4 style="color:{IBCF_COLOR};margin-top:0">
        IBCF Reasoning
        </h4>
        """,
        unsafe_allow_html=True
    )

    if not ibcf_recs.empty:

        selected_ibcf_product = st.selectbox(
            "IBCF Recommendation",
            ibcf_recs["product_name"].tolist(),
            key="ibcf_explain"
        )

        ibcf_row = ibcf_recs[
            ibcf_recs["product_name"]
            == selected_ibcf_product
        ].iloc[0]

        st.metric(
            "Recommendation Score",
            round(
                ibcf_row["recommendation_score"],
                3
            )
        )

        st.markdown(
            "#### Contributing Products"
        )

        contrib_products = ibcf_row.get(
            "contributing_products",
            []
        )

        if isinstance(
            contrib_products,
            list
        ):

            chips = ""

            for p in contrib_products:

                chips += f"""
                <span class="chip">
                {p}
                </span>
                """

            st.markdown(
                chips,
                unsafe_allow_html=True
            )

        st.markdown("#### Explanation")

        st.write(
            ibcf_row.get("reason", "")
        )

    else:

        st.info("No IBCF explanations available.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Recommendation Overlap Analysis
# ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="section-header">Recommendation Overlap Analysis</div>',
    unsafe_allow_html=True
)

cust_overlap = overlap_df[
    overlap_df["customer_id"] == selected_customer
]

if not cust_overlap.empty:

    overlap_row = cust_overlap.iloc[0]

    overlap_ratio = overlap_row["overlap_ratio"]
    intersection_size = overlap_row["intersection_size"]
    union_size = overlap_row["union_size"]

    fp_products = overlap_row["fp_products"]
    ibcf_products = overlap_row["ibcf_products"]

    common_products = sorted([
        product_map.get(pid, pid)
        for pid in set(fp_products).intersection(set(ibcf_products))
    ])

    fp_only = sorted([
        product_map.get(pid, pid)
        for pid in set(fp_products).difference(set(ibcf_products))
    ])

    ibcf_only = sorted([
        product_map.get(pid, pid)
        for pid in set(ibcf_products).difference(set(fp_products))
    ])

    k1,k2,k3,k4 = st.columns(4)

    metrics = [

        (
            "Overlap %",
            f"{overlap_ratio:.1%}",
            ACCENT_AMBER
        ),

        (
            "Common Products",
            intersection_size,
            ACCENT_TEAL
        ),

        (
            "FP Only",
            len(fp_only),
            FP_COLOR
        ),

        (
            "IBCF Only",
            len(ibcf_only),
            IBCF_COLOR
        )
    ]

    for col, metric in zip(
        [k1,k2,k3,k4],
        metrics
    ):

        label,value,color = metric

        col.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value" style="color:{color}">
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

    overlap_left, overlap_mid, overlap_right = st.columns(3)

    # --------------------------------------------------------
    # Common Products
    # --------------------------------------------------------

    with overlap_left:

        st.markdown(
            f"""
            <div class="kpi-card">
            <h4 style="color:{ACCENT_TEAL}">
            Common Recommendations
            </h4>
            """,
            unsafe_allow_html=True
        )

        if common_products:

            chips = ""

            for p in common_products:

                chips += f"""
                <span class="chip">
                {p}
                </span>
                """

            st.markdown(
                chips,
                unsafe_allow_html=True
            )

        else:

            st.info("No common products")

        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # FP Only
    # --------------------------------------------------------

    with overlap_mid:

        st.markdown(
            f"""
            <div class="kpi-card">
            <h4 style="color:{FP_COLOR}">
            FP Only
            </h4>
            """,
            unsafe_allow_html=True
        )

        if fp_only:

            chips = ""

            for p in fp_only:

                chips += f"""
                <span class="chip">
                {p}
                </span>
                """

            st.markdown(
                chips,
                unsafe_allow_html=True
            )

        else:

            st.info("No FP-exclusive products")

        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # IBCF Only
    # --------------------------------------------------------

    with overlap_right:

        st.markdown(
            f"""
            <div class="kpi-card">
            <h4 style="color:{IBCF_COLOR}">
            IBCF Only
            </h4>
            """,
            unsafe_allow_html=True
        )

        if ibcf_only:

            chips = ""

            for p in ibcf_only:

                chips += f"""
                <span class="chip">
                {p}
                </span>
                """

            st.markdown(
                chips,
                unsafe_allow_html=True
            )

        else:

            st.info("No IBCF-exclusive products")

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Similar Customers
# ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="section-header">Similar Customers</div>',
    unsafe_allow_html=True
)

segment_customers = c360[
    c360["customer_segment"]
    == cust["customer_segment"]
].copy()

segment_customers = segment_customers[
    segment_customers["customer_id"]
    != selected_customer
]

if not segment_customers.empty:

    income_std = max(
        c360["annual_income"].std(),
        1
    )

    engagement_std = max(
        c360["engagement_score"].std(),
        1
    )

    risk_std = max(
        c360["risk_score"].std(),
        1
    )

    segment_customers["similarity"] = (

        1 / (
            1 +
            abs(
                segment_customers["annual_income"]
                - cust["annual_income"]
            ) / income_std
        )

        +

        1 / (
            1 +
            abs(
                segment_customers["engagement_score"]
                - cust["engagement_score"]
            ) / engagement_std
        )

        +

        1 / (
            1 +
            abs(
                segment_customers["risk_score"]
                - cust["risk_score"]
            ) / risk_std
        )

    )

    similar_customers = (

        segment_customers
        .sort_values(
            "similarity",
            ascending=False
        )
        .head(5)

    )

    display_cols = [

        "customer_id",
        "customer_name",
        "annual_income",
        "engagement_score",
        "risk_score",
        "similarity"

    ]

    st.dataframe(

        similar_customers[
            display_cols
        ].round(
            {"similarity":3}
        ),

        use_container_width=True,
        hide_index=True

    )

else:

    st.info(
        "No comparable customers found."
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Peer Comparison
# ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="section-header">Customer vs Peer Average</div>',
    unsafe_allow_html=True
)

peer_df = c360[
    c360["customer_segment"]
    == cust["customer_segment"]
]

peer_income = peer_df["annual_income"].mean()
peer_engagement = peer_df["engagement_score"].mean()
peer_risk = peer_df["risk_score"].mean()

peer_tenure = peer_df["tenure_months"].mean()

p1,p2,p3,p4 = st.columns(4)

comparison_metrics = [

    (
        "Income",
        f"₹{cust['annual_income']:,.0f}",
        f"Peer Avg ₹{peer_income:,.0f}"
    ),

    (
        "Engagement",
        round(cust["engagement_score"],2),
        round(peer_engagement,2)
    ),

    (
        "Risk",
        round(cust["risk_score"],2),
        round(peer_risk,2)
    ),

    (
        "Tenure",
        round(cust["tenure_months"],1),
        round(peer_tenure,1)
    )

]

for col, metric in zip(
    [p1,p2,p3,p4],
    comparison_metrics
):

    label,value,peer = metric

    col.metric(
        label,
        value,
        delta=f"Peer: {peer}"
    )

st.markdown("<br>", unsafe_allow_html=True)