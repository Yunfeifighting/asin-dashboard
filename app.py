import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import api

st.set_page_config(
    page_title="ASIN Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e8ecf0;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
  }
  [data-testid="stMetricLabel"] { font-size: 12px; color: #64748b; font-weight: 500; }
  [data-testid="stMetricValue"] { font-size: 26px; font-weight: 700; color: #0f172a; }
  [data-testid="stMetricDelta"] { font-size: 12px; }
  hr { margin: 8px 0; border-color: #f1f5f9; }
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 4px;
  }
  .badge-prime { background: #dbeafe; color: #1d4ed8; }
  .badge-fba   { background: #fef3c7; color: #92400e; }
  .badge-asin  { background: #ede9fe; color: #5b21b6; font-family: monospace; }
  .product-header {
    background: white;
    border: 1px solid #e8ecf0;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
    margin-bottom: 16px;
  }
  .comp-row {
    background: white;
    border: 1px solid #f1f5f9;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
  }
</style>
""", unsafe_allow_html=True)


def get_api_keys():
    rf_key = st.secrets.get("RAINFOREST_API_KEY", "") if hasattr(st, "secrets") else ""
    ka_key = st.secrets.get("KEEPA_API_KEY", "") if hasattr(st, "secrets") else ""
    with st.sidebar:
        st.markdown("### API Keys")
        st.caption("Pre-configured in secrets - no manual entry needed")
        rf_key = st.text_input("Rainforest API Key", value=rf_key, type="password")
        ka_key = st.text_input("Keepa API Key", value=ka_key, type="password")
        st.divider()
        st.markdown("### How to use")
        st.markdown("""
1. Enter ASIN (10-char alphanumeric)
2. Click **Search**
3. Data loads in 3-8 seconds

**Data Sources**
- Rainforest API: real-time product page
- Keepa API: 7-day history / 90-day stats
        """)
    return rf_key, ka_key


@st.cache_data(ttl=300, show_spinner=False)
def load_data(asin, rf_key, ka_key):
    errors = {}
    product, competitors = {}, []
    try:
        product = api.fetch_product(asin, rf_key)
        if product.get("brand"):
            search_term = f"{product['brand']} {product.get('bsr_category','')}"
            try:
                competitors = api.fetch_competitors(search_term, rf_key, asin)
            except Exception as e:
                errors["competitors"] = str(e)
    except Exception as e:
        errors["rainforest"] = str(e)
    keepa = {}
    try:
        keepa = api.fetch_keepa(asin, ka_key)
    except Exception as e:
        errors["keepa"] = str(e)
    return product, keepa, competitors, errors


def last_7_days_labels():
    today = datetime.today()
    return [(today - timedelta(days=6 - i)).strftime("%-m/%-d") for i in range(7)]


def trend_chart(values, labels, title, color, reverse_color=False):
    has_data = any(v is not None for v in values)
    if not has_data:
        fig = go.Figure()
        fig.add_annotation(text="No historical data", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=13, color="#94a3b8"))
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=labels, y=values,
            mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline"),
            marker=dict(size=6, color=color, line=dict(width=2, color="white")),
            connectgaps=False,
            hovertemplate="%{x}<br>" + title + ": " +
                          ("%{y:,.0f}" if "BSR" in title else "$%{y:.2f}") +
                          "<extra></extra>",
        ))
        clean = [v for v in values if v is not None]
        if len(clean) >= 2:
            pct = (clean[-1] - clean[0]) / clean[0] * 100
            if reverse_color:
                arrow = "Rank up" if pct < 0 else "Rank down"
                arrow_color = "#22c55e" if pct < 0 else "#ef4444"
            else:
                arrow = f"+{abs(pct):.1f}%" if pct > 0 else f"-{abs(pct):.1f}%"
                arrow_color = "#22c55e" if pct > 0 else "#ef4444"
            fig.add_annotation(
                text=f"<b>{arrow}</b>",
                xref="paper", yref="paper", x=1.0, y=1.08,
                showarrow=False, xanchor="right",
                font=dict(size=12, color=arrow_color),
            )
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#374151"), x=0),
        margin=dict(l=0, r=0, t=36, b=0),
        height=180,
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#94a3b8")),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9",
                   tickfont=dict(size=11, color="#94a3b8"),
                   tickformat=",.0f" if "BSR" in title else "$.2f"),
        showlegend=False,
        hoverlabel=dict(bgcolor="#1e293b", font_color="white", font_size=12),
    )
    return fig


def price_range_gauge(current, p_min, p_avg, p_max):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current or 0,
        delta={"reference": p_avg, "valueformat": ".2f",
               "prefix": "vs avg $", "increasing": {"color": "#ef4444"},
               "decreasing": {"color": "#22c55e"}},
        number={"prefix": "$", "valueformat": ".2f",
                "font": {"size": 28, "color": "#0f172a"}},
        gauge={
            "axis": {"range": [p_min, p_max], "tickformat": "$.0f",
                     "tickfont": {"size": 10}},
            "bar": {"color": "#6366f1", "thickness": 0.3},
            "bgcolor": "white",
            "steps": [
                {"range": [p_min, p_avg], "color": "#d1fae5"},
                {"range": [p_avg, p_max], "color": "#fee2e2"},
            ],
            "threshold": {
                "line": {"color": "#f59e0b", "width": 3},
                "thickness": 0.75,
                "value": p_avg,
            },
        },
    ))
    fig.update_layout(
        height=160, margin=dict(l=20, r=20, t=10, b=0),
        paper_bgcolor="white",
        font={"color": "#374151"},
    )
    return fig

def render_product_header(asin, product, keepa):
    price = product.get("current_price") or keepa.get("current_price")
    rating = product.get("rating") or keepa.get("rating")
    reviews = product.get("review_count") or keepa.get("review_count")
    is_prime = product.get("is_prime", False)
    is_fba = product.get("is_fba", False)
    title = product.get("title") or f"ASIN: {asin}"
    brand = product.get("brand", "")
    img = product.get("main_image", "")

    col_img, col_info = st.columns([1, 5])
    with col_img:
        if img:
            st.image(img, width=120)
    with col_info:
        badges = f'<span class="badge badge-asin">{asin}</span>'
        if is_prime:
            badges += '<span class="badge badge-prime">Prime</span>'
        if is_fba:
            badges += '<span class="badge badge-fba">FBA</span>'
        st.markdown(badges, unsafe_allow_html=True)
        st.markdown(f"### {title}")
        meta_parts = []
        if brand:
            meta_parts.append(f"**{brand}**")
        if rating:
            stars = "★" * int(round(rating))
            meta_parts.append(f"{stars} {rating}")
        if reviews:
            meta_parts.append(f"{reviews:,} reviews")
        if product.get("variant_count"):
            meta_parts.append(f"{product['variant_count']} variants")
        if product.get("img_count"):
            meta_parts.append(f"{product['img_count']} images")
        st.caption("  ·  ".join(meta_parts))


def render_metrics(product, keepa):
    price = product.get("current_price") or keepa.get("current_price")
    bsr = product.get("bsr") or keepa.get("current_bsr")
    reviews = product.get("review_count") or keepa.get("review_count")
    rating = product.get("rating") or keepa.get("rating")
    monthly = keepa.get("monthly_sold")
    p_min = keepa.get("price_90d_min")
    p_max = keepa.get("price_90d_max")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        delta = None
        if price and p_min:
            delta = f"vs 90d low +${price - p_min:.2f}"
        st.metric("Price", f"${price:.2f}" if price else "—", delta=delta)
    with c2:
        bsr_cat = (product.get("bsr_category") or "")[:18]
        st.metric("BSR Rank", f"#{bsr:,}" if bsr else "—", delta=bsr_cat or None)
    with c3:
        st.metric("Rating", f"{rating} / 5.0" if rating else "—",
                  delta=f"{reviews:,} reviews" if reviews else None)
    with c4:
        st.metric("Est. Monthly Sales", f"~{monthly:,}" if monthly else "—",
                  delta="Source: Keepa")
    with c5:
        avg = keepa.get("price_90d_avg")
        st.metric("90-Day Avg Price", f"${avg:.2f}" if avg else "—",
                  delta=f"Range ${p_min:.2f}–${p_max:.2f}" if p_min and p_max else None)


def render_trends(keepa):
    price_7d = keepa.get("price_7d", [None] * 7)
    bsr_7d = keepa.get("bsr_7d", [None] * 7)
    labels = last_7_days_labels()
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.plotly_chart(
                trend_chart(price_7d, labels, "7-Day Price Trend", "#6366f1"),
                use_container_width=True, config={"displayModeBar": False},
            )
    with col2:
        with st.container(border=True):
            st.plotly_chart(
                trend_chart(bsr_7d, labels, "7-Day BSR Trend", "#f59e0b", reverse_color=True),
                use_container_width=True, config={"displayModeBar": False},
            )
    with st.expander("Daily Breakdown (7 days)", expanded=False):
        rows = []
        for i, day in enumerate(labels):
            p = price_7d[i]
            b = bsr_7d[i]
            rows.append({"Date": day, "Price": f"${p:.2f}" if p else "—",
                         "BSR": f"#{b:,}" if b else "—"})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def render_price_stats(keepa, product):
    p_min = keepa.get("price_90d_min")
    p_avg = keepa.get("price_90d_avg")
    p_max = keepa.get("price_90d_max")
    current = product.get("current_price") or keepa.get("current_price")
    if not (p_min and p_avg and p_max):
        return
    with st.container(border=True):
        st.markdown("**90-Day Price Range**")
        col_gauge, col_stat = st.columns([3, 2])
        with col_gauge:
            st.plotly_chart(
                price_range_gauge(current, p_min, p_avg, p_max),
                use_container_width=True, config={"displayModeBar": False},
            )
        with col_stat:
            st.markdown("")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Low", f"${p_min:.2f}")
            mc2.metric("Avg", f"${p_avg:.2f}")
            mc3.metric("High", f"${p_max:.2f}")
            if current and p_min and p_max:
                pct = (current - p_min) / (p_max - p_min) * 100 if p_max != p_min else 50
                st.progress(int(min(100, max(0, pct))),
                            text=f"Current price at **{pct:.0f}%** of 90-day range")


def render_bsr_breakdown(product):
    all_bsr = product.get("all_bsr") or []
    if not all_bsr:
        return
    with st.container(border=True):
        st.markdown("**BSR by Category**")
        rows = [{"Category": b["category"], "Rank": f"#{b['rank']:,}"} for b in all_bsr]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def render_bullets(product):
    bullets = product.get("feature_bullets") or []
    if not bullets:
        return
    with st.expander("Feature Bullets", expanded=True):
        for b in bullets:
            st.markdown(f"- {b}")


def render_competitors(competitors, my_price):
    if not competitors:
        return
    st.markdown("### Competitor ASIN Comparison")
    cols = st.columns(len(competitors))
    for i, c in enumerate(competitors):
        with cols[i]:
            with st.container(border=True):
                if c.get("thumbnail"):
                    st.image(c["thumbnail"], width=80)
                asin_str = c.get("asin", "")
                st.caption(f"`{asin_str}`")
                price = c.get("price")
                if price:
                    diff = price - my_price if my_price else 0
                    color = "U0001f7e2" if diff > 0 else "U0001f534"
                    diff_str = f"{color} {'+' if diff > 0 else ''}{diff:.2f}"
                    st.metric("Price", f"${price:.2f}", delta=diff_str)
                else:
                    st.metric("Price", "—")
                rating = c.get("rating")
                reviews = c.get("review_count")
                st.caption(f"★ {rating or '—'}  ·  {f'{reviews:,}' if reviews else '—'} reviews")
                st.caption((c.get("title") or "")[:50] + "…")
    with st.expander("Competitor Detail Table", expanded=False):
        rows = []
        if my_price:
            rows.append({
                "ASIN": f"**{st.session_state.get('asin','—')} (mine)**",
                "Price": f"${my_price:.2f}", "Rating": "—", "Reviews": "—", "Prime": "—"
            })
        for c in competitors:
            p = c.get("price")
            rows.append({
                "ASIN": c.get("asin", ""),
                "Price": f"${p:.2f}" if p else "—",
                "Rating": c.get("rating") or "—",
                "Reviews": f"{c['review_count']:,}" if c.get("review_count") else "—",
                "Prime": "✅" if c.get("is_prime") else "❌",
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def render_error_banner(errors):
    if not errors:
        return
    with st.expander("Data source errors", expanded=True):
        for src, msg in errors.items():
            st.error(f"**{src}**: {msg}")


def main():
    rf_key, ka_key = get_api_keys()
    st.markdown(
        "<h2 style='margin-bottom:4px'>Amazon ASIN Dashboard</h2>"
        "<p style='color:#64748b;font-size:14px;margin-bottom:16px'>"
        "Enter any Amazon US ASIN for price trends, BSR rankings, and competitor analysis</p>",
        unsafe_allow_html=True,
    )
    col_input, col_btn, col_spacer = st.columns([3, 1, 4])
    with col_input:
        asin_input = st.text_input(
            "ASIN", placeholder="B0D54LVZK5", max_chars=10,
            label_visibility="collapsed",
        ).strip().upper()
    with col_btn:
        search = st.button("Search", type="primary", use_container_width=True)
    st.markdown("<p style='font-size:12px;color:#94a3b8'>Examples:</p>", unsafe_allow_html=True)
    ex_cols = st.columns(4)
    examples = ["B0D54LVZK5", "B08N5WRWNW", "B07FZ8S74R", "B09B8ZCPKQ"]
    for i, ex in enumerate(examples):
        if ex_cols[i].button(ex, key=f"ex_{ex}", use_container_width=True):
            asin_input = ex
            search = True
    st.divider()
    if not search and "last_asin" not in st.session_state:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;color:#94a3b8">
            <div style="font-size:48px">U0001f4e6</div>
            <div style="font-size:18px;margin-top:12px;color:#64748b;font-weight:600">
                Enter an ASIN to begin
            </div>
            <div style="font-size:13px;margin-top:8px">
                Supports all Amazon.com products with live data
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    if search and asin_input:
        st.session_state["last_asin"] = asin_input
    asin = st.session_state.get("last_asin", asin_input)
    if not asin or len(asin) != 10:
        st.warning("ASIN must be 10 alphanumeric characters, e.g. B0D54LVZK5")
        return
    if not rf_key or not ka_key:
        st.error("Please enter API Keys in the sidebar, or configure in secrets.toml")
        return
    st.session_state["asin"] = asin
    with st.spinner(f"Loading {asin} data from Rainforest + Keepa APIs..."):
        product, keepa, competitors, errors = load_data(asin, rf_key, ka_key)
    if errors:
        render_error_banner(errors)
    with st.container(border=True):
        render_product_header(asin, product, keepa)
    render_metrics(product, keepa)
    st.markdown("")
    col_l, col_r = st.columns([2, 3])
    with col_l:
        render_price_stats(keepa, product)
    with col_r:
        render_trends(keepa)
    col_bsr, col_bullets = st.columns(2)
    with col_bsr:
        render_bsr_breakdown(product)
    with col_bullets:
        render_bullets(product)
    my_price = product.get("current_price") or keepa.get("current_price")
    render_competitors(competitors, my_price)
    st.markdown("---")
    fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tokens = keepa.get("tokens_left")
    st.caption(
        f"Updated: {fetch_time}  ·  ASIN: `{asin}`"
        + (f"  ·  Keepa tokens left: {tokens:,}" if tokens else "")
    )


if __name__ == "__main__":
    main()
