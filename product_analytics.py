import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Product Analytics · RecoIQ",
    page_icon="📦",
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
      font-size: 0.68rem; font-weight: 600; letter-spacing: 0.14em;
      text-transform: uppercase; color: {ACCENT_TEAL}; margin-bottom: 4px;
  }}
  .page-title {{
      font-size: 1.8rem; font-weight: 800; color: {TEXT_PRIMARY}; margin: 0 0 4px 0;
  }}
  .page-subtitle {{
      font-size: 0.85rem; color: {TEXT_MUTED}; margin-bottom: 0;
  }}
  .section-header {{
      font-size: 0.7rem; font-weight: 600; color: {TEXT_MUTED};
      text-transform: uppercase; letter-spacing: 0.12em;
      border-bottom: 1px solid {PANEL_BORDER}; padding-bottom: 6px; margin-bottom: 16px;
  }}
  .kpi-card {{
      background: {PANEL_BG}; border: 1px solid {PANEL_BORDER};
      border-radius: 10px; padding: 18px 22px;
  }}
  .kpi-value {{ font-size: 1.9rem; font-weight: 800; line-height: 1.1; }}
  .kpi-label {{
      font-size: 0.72rem; color: {TEXT_MUTED}; text-transform: uppercase;
      letter-spacing: 0.08em; margin-top: 4px;
  }}
  .kpi-sub {{ font-size: 0.72rem; color: {TEXT_MUTED}; margin-top: 5px; }}
  .chart-panel {{
      background: {PANEL_BG}; border: 1px solid {PANEL_BORDER};
      border-radius: 10px; padding: 20px;
  }}
  .product-card {{
      background: {PANEL_BG}; border: 1px solid {PANEL_BORDER};
      border-radius: 10px; padding: 18px 22px; margin-bottom: 10px;
  }}
  .product-card-name {{
      font-size: 1rem; font-weight: 700; color: {TEXT_PRIMARY}; margin-bottom: 10px;
  }}
  .product-stat-row {{
      display: flex; justify-content: space-between;
      padding: 6px 0; border-bottom: 1px solid {PANEL_BORDER}; font-size: 0.8rem;
  }}
  .product-stat-row:last-child {{ border-bottom: none; }}
  .product-stat-label {{ color: {TEXT_MUTED}; }}
  .product-stat-value {{ font-weight: 700; color: {TEXT_PRIMARY}; }}
  .rank-pill {{
      display: inline-block; font-size: 0.65rem; font-weight: 700;
      letter-spacing: 0.08em; text-transform: uppercase;
      padding: 2px 8px; border-radius: 20px; margin-left: 8px;
  }}
  div[data-testid="stPlotlyChart"] {{ background: transparent !important; }}
</style>
""", unsafe_allow_html=True)

# ── Data Loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_product_comparison():
    return pd.read_csv(
        "data/product_recommendation_comparison.csv"
    )


@st.cache_data(ttl=300, show_spinner=False)
def load_all_recommendations():
    return pd.read_csv(
        "data/all_recommendations.csv"
    )


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
def load_products():
    return pd.read_csv(
        "data/products.csv"
    )

with st.spinner("Loading product data…"):
    try:
        prod_cmp  = load_product_comparison()
        all_recs  = load_all_recommendations()
        c360      = load_customer_360()
        products  = load_products()
        load_ok   = True
    except Exception as e:
        st.error(f"Data load failed: {e}")
        load_ok = False

if not load_ok:
    st.stop()

# ── Derived metrics ───────────────────────────────────────────────────────────
prod_cmp["total_recs"] = prod_cmp.get("fp_count", 0) + prod_cmp.get("ibcf_count", 0)

# Ownership counts from customer_360
owned_counts = {}
for _, row in c360.iterrows():
    for p in row["owned_products"]:
        p = p.strip()
        owned_counts[p] = owned_counts.get(p, 0) + 1
ownership_df = pd.DataFrame(list(owned_counts.items()), columns=["product_name", "ownership_count"])

# Merge ownership into product comparison
prod_merged = prod_cmp.merge(ownership_df, on="product_name", how="left").fillna(0)
prod_merged["ownership_count"] = prod_merged["ownership_count"].astype(int)

# Recommendation rate: recs / owners (demand signal)
prod_merged["rec_per_owner"] = prod_merged.apply(
    lambda r: r["total_recs"] / r["ownership_count"] if r["ownership_count"] > 0 else 0, axis=1
)

# Product → segment mapping from all_recs
seg_prod = pd.DataFrame()
if not all_recs.empty and "product_name" in all_recs.columns:
    recs_seg = all_recs.merge(
        c360[["customer_id", "customer_segment"]], on="customer_id", how="left"
    )
    seg_prod = (
        recs_seg.groupby(["product_name", "customer_segment"])
        .size().reset_index(name="count")
    )

all_products = sorted(prod_merged["product_name"].dropna().unique().tolist())

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='font-size:1.1rem;font-weight:800;color:{ACCENT_TEAL};margin-bottom:4px'>RecoIQ</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.7rem;color:{TEXT_MUTED};margin-bottom:24px'>Recommendation Intelligence Platform</div>", unsafe_allow_html=True)
    st.markdown("---")
    selected_product = st.selectbox("Focus Product", ["All Products"] + all_products)
    st.markdown("---")
    top_n = st.slider("Top N Products", 5, 25, 12)
    sort_by = st.selectbox("Sort Charts By", ["Total Recs", "FP Count", "IBCF Count", "Ownership", "Rec per Owner"])
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.72rem;color:{TEXT_MUTED}'>Catalog size</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1.3rem;font-weight:800;color:{ACCENT_TEAL}'>{len(all_products)} products</div>", unsafe_allow_html=True)

sort_col_map = {
    "Total Recs":     "total_recs",
    "FP Count":       "fp_count",
    "IBCF Count":     "ibcf_count",
    "Ownership":      "ownership_count",
    "Rec per Owner":  "rec_per_owner",
}
sort_col = sort_col_map[sort_by]

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown('<div class="page-eyebrow">Catalog Intelligence</div>', unsafe_allow_html=True)
st.markdown('<p class="page-title">Product Analytics</p>', unsafe_allow_html=True)
st.markdown(f'<p class="page-subtitle">Ownership depth, recommendation reach, and cross-engine demand signals across {len(all_products)} products</p>', unsafe_allow_html=True)
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

total_catalog   = len(all_products)
total_ownership = int(prod_merged["ownership_count"].sum())
total_fp        = int(prod_merged["fp_count"].sum()) if "fp_count" in prod_merged.columns else 0
total_ibcf      = int(prod_merged["ibcf_count"].sum()) if "ibcf_count" in prod_merged.columns else 0
top_product     = prod_merged.sort_values("total_recs", ascending=False).iloc[0]["product_name"] if not prod_merged.empty else "—"

kpi(k1, total_catalog,         "Catalog Size",          ACCENT_TEAL)
kpi(k2, f"{total_ownership:,}","Total Ownerships",      ACCENT_VIOLET)
kpi(k3, f"{total_fp:,}",       "Total FP Recs",         FP_COLOR,    f"across catalog")
kpi(k4, f"{total_ibcf:,}",     "Total IBCF Recs",       IBCF_COLOR,  f"across catalog")
kpi(k5, top_product,           "Most Recommended",       ACCENT_AMBER)

st.markdown("<br>", unsafe_allow_html=True)

# ── If a single product is focused ────────────────────────────────────────────
if selected_product != "All Products":
    p_row = prod_merged[prod_merged["product_name"] == selected_product]
    if not p_row.empty:
        p = p_row.iloc[0]

        st.markdown('<div class="section-header">Product Deep Dive</div>', unsafe_allow_html=True)
        d1, d2, d3, d4 = st.columns(4)
        kpi(d1, f"{int(p.get('ownership_count', 0)):,}", "Customers Own This",  ACCENT_TEAL)
        kpi(d2, f"{int(p.get('fp_count', 0)):,}",        "FP-Growth Recs",      FP_COLOR)
        kpi(d3, f"{int(p.get('ibcf_count', 0)):,}",      "IBCF Recs",           IBCF_COLOR)
        kpi(d4, f"{p.get('rec_per_owner', 0):.2f}",      "Recs per Owner",      ACCENT_AMBER)

        st.markdown("<br>", unsafe_allow_html=True)

        # Segment breakdown for this product
        if not seg_prod.empty:
            prod_seg_data = seg_prod[seg_prod["product_name"] == selected_product].sort_values("count", ascending=True)
            if not prod_seg_data.empty:
                st.markdown('<div class="section-header">Recommendation Demand by Segment</div>', unsafe_allow_html=True)
                colors = [SEGMENT_COLORS.get(s, "#8B949E") for s in prod_seg_data["customer_segment"]]
                fig_seg = go.Figure(go.Bar(
                    x=prod_seg_data["count"],
                    y=prod_seg_data["customer_segment"],
                    orientation="h",
                    marker_color=colors,
                    marker_line_width=0,
                    text=prod_seg_data["count"],
                    textposition="outside",
                    textfont=dict(color=TEXT_MUTED, size=11),
                ))
                fig_seg.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=260,
                    margin=dict(l=10, r=40, t=10, b=10),
                    xaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
                               tickfont=dict(color=TEXT_MUTED),
                               title=dict(text="Times Recommended", font=dict(color=TEXT_MUTED, size=11))),
                    yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_PRIMARY, size=12)),
                    showlegend=False,
                )
                st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
                st.plotly_chart(fig_seg, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

    # co-recommended products
    if not all_recs.empty and "product_name" in all_recs.columns:
        customers_who_got_rec = all_recs[
            all_recs["product_name"] == selected_product
        ]["customer_id"].unique()

        co_recs = all_recs[
            (all_recs["customer_id"].isin(customers_who_got_rec)) &
            (all_recs["product_name"] != selected_product)
        ]
        if not co_recs.empty:
            st.markdown('<div class="section-header">Frequently Co-Recommended With</div>', unsafe_allow_html=True)
            co_counts = (
                co_recs.groupby("product_name").size()
                .reset_index(name="co_count")
                .sort_values("co_count", ascending=True)
                .tail(top_n)
            )
            fig_co = go.Figure(go.Bar(
                x=co_counts["co_count"],
                y=co_counts["product_name"],
                orientation="h",
                marker_color=ACCENT_VIOLET,
                marker_line_width=0,
                text=co_counts["co_count"],
                textposition="outside",
                textfont=dict(color=TEXT_MUTED, size=10),
            ))
            fig_co.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=max(220, len(co_counts) * 32),
                margin=dict(l=10, r=40, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
                           tickfont=dict(color=TEXT_MUTED),
                           title=dict(text="Co-recommendation count", font=dict(color=TEXT_MUTED, size=11))),
                yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_PRIMARY, size=11)),
                showlegend=False,
            )
            st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
            st.plotly_chart(fig_co, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

# ── All-products view ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Recommendation Reach · All Products</div>', unsafe_allow_html=True)

top_prods = prod_merged.sort_values(sort_col, ascending=False).head(top_n).sort_values(sort_col, ascending=True)

fig_reach = go.Figure()
for col_name, color, label in [("fp_count", FP_COLOR, "FP-Growth"), ("ibcf_count", IBCF_COLOR, "IBCF")]:
    if col_name in top_prods.columns:
        fig_reach.add_trace(go.Bar(
            name=label,
            x=top_prods[col_name],
            y=top_prods["product_name"],
            orientation="h",
            marker_color=color,
            marker_line_width=0,
        ))
fig_reach.update_layout(
    barmode="stack",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=max(300, top_n * 30),
    margin=dict(l=10, r=30, t=10, b=10),
    legend=dict(font=dict(color=TEXT_PRIMARY), bgcolor="rgba(0,0,0,0)",
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
               tickfont=dict(color=TEXT_MUTED),
               title=dict(text="Total Recommendations", font=dict(color=TEXT_MUTED, size=11))),
    yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_PRIMARY, size=11)),
)
st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
st.plotly_chart(fig_reach, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Ownership vs Recommendation scatter ───────────────────────────────────────
st.markdown('<div class="section-header">Ownership vs Recommendation Demand</div>', unsafe_allow_html=True)

fig_ov = go.Figure()
fig_ov.add_trace(go.Scatter(
    x=prod_merged["ownership_count"],
    y=prod_merged["total_recs"],
    mode="markers+text",
    text=prod_merged["product_name"],
    textposition="top center",
    textfont=dict(color=TEXT_MUTED, size=9),
    marker=dict(
        color=prod_merged["rec_per_owner"],
        colorscale=[[0, IBCF_COLOR], [0.5, ACCENT_AMBER], [1, FP_COLOR]],
        size=prod_merged["total_recs"].apply(lambda v: max(8, min(28, v / 20))),
        showscale=True,
        colorbar=dict(
            title=dict(text="Recs / Owner", font=dict(color=TEXT_MUTED, size=10)),
            tickfont=dict(color=TEXT_MUTED, size=9),
            outlinewidth=0,
            bgcolor="rgba(0,0,0,0)",
        ),
        line=dict(width=0),
        opacity=0.85,
    ),
    hovertemplate=(
        "<b>%{text}</b><br>"
        "Owners: %{x}<br>"
        "Total Recs: %{y}<extra></extra>"
    ),
))
fig_ov.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=420,
    margin=dict(l=10, r=20, t=10, b=10),
    xaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
               tickfont=dict(color=TEXT_MUTED),
               title=dict(text="Customers Who Own Product", font=dict(color=TEXT_MUTED, size=11))),
    yaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
               tickfont=dict(color=TEXT_MUTED),
               title=dict(text="Total Recommendations Generated", font=dict(color=TEXT_MUTED, size=11))),
    showlegend=False,
)
st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
st.plotly_chart(fig_ov, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)
st.markdown(f"<div style='font-size:0.75rem;color:{TEXT_MUTED};margin-top:6px'>Bubble size = total recommendations. Colour = recommendations per owner (violet → amber → teal). Products in the upper-left are high-demand relative to ownership.</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Recs per owner ranking ────────────────────────────────────────────────────
st.markdown('<div class="section-header">Recommendation Intensity · Recs per Owner</div>', unsafe_allow_html=True)

rpo = prod_merged[prod_merged["ownership_count"] > 0].sort_values("rec_per_owner", ascending=False).head(top_n).sort_values("rec_per_owner", ascending=True)

fig_rpo = go.Figure(go.Bar(
    x=rpo["rec_per_owner"].round(2),
    y=rpo["product_name"],
    orientation="h",
    marker=dict(
        color=rpo["rec_per_owner"],
        colorscale=[[0, IBCF_COLOR], [1, ACCENT_TEAL]],
        showscale=False,
    ),
    marker_line_width=0,
    text=rpo["rec_per_owner"].round(2),
    textposition="outside",
    textfont=dict(color=TEXT_MUTED, size=10),
))
fig_rpo.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=max(280, top_n * 30),
    margin=dict(l=10, r=60, t=10, b=10),
    xaxis=dict(showgrid=True, gridcolor=PANEL_BORDER, zeroline=False,
               tickfont=dict(color=TEXT_MUTED),
               title=dict(text="Recommendations per Owner", font=dict(color=TEXT_MUTED, size=11))),
    yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_PRIMARY, size=11)),
    showlegend=False,
)
st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
st.plotly_chart(fig_rpo, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Segment heatmap ───────────────────────────────────────────────────────────
if not seg_prod.empty:
    st.markdown('<div class="section-header">Product × Segment Recommendation Heatmap</div>', unsafe_allow_html=True)

    heatmap_pivot = seg_prod.pivot_table(
        index="product_name", columns="customer_segment", values="count", fill_value=0
    )
    # limit to top products by total
    top_heat_prods = prod_merged.sort_values("total_recs", ascending=False).head(top_n)["product_name"].tolist()
    heatmap_pivot  = heatmap_pivot.reindex([p for p in top_heat_prods if p in heatmap_pivot.index])

    fig_heat = go.Figure(go.Heatmap(
        z=heatmap_pivot.values,
        x=list(heatmap_pivot.columns),
        y=list(heatmap_pivot.index),
        colorscale=[
            [0.0,  DARK_BG],
            [0.01, "#1a2332"],
            [0.3,  IBCF_COLOR],
            [0.7,  ACCENT_TEAL],
            [1.0,  "#ffffff"],
        ],
        showscale=True,
        colorbar=dict(
            title=dict(text="Rec Count", font=dict(color=TEXT_MUTED, size=10)),
            tickfont=dict(color=TEXT_MUTED, size=9),
            outlinewidth=0,
            bgcolor="rgba(0,0,0,0)",
        ),
        hovertemplate="Product: %{y}<br>Segment: %{x}<br>Recs: %{z}<extra></extra>",
    ))
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=max(350, top_n * 32),
        margin=dict(l=10, r=20, t=10, b=10),
        xaxis=dict(tickfont=dict(color=TEXT_MUTED, size=11), side="bottom"),
        yaxis=dict(tickfont=dict(color=TEXT_PRIMARY, size=11), autorange="reversed"),
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)