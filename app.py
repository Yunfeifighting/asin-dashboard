"""
ASIN Dashboard — Streamlit 版本
分享方式：推送到 GitHub → 部署到 share.streamlit.io（免费）
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import api  # api.py 同目录

# ═══════════════════════════════════════════════════════════════
#  页面配置
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ASIN Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 自定义 CSS ──────────────────────────────────────────────────
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
  .score-bar-wrap { background:#f1f5f9; border-radius:99px; height:10px; margin:6px 0; }
  .score-bar      { height:10px; border-radius:99px; }
  .priority-critical { color:#dc2626; font-weight:700; }
  .priority-high     { color:#ea580c; font-weight:600; }
  .priority-medium   { color:#d97706; font-weight:600; }
  .priority-low      { color:#2563eb; font-weight:500; }
  .priority-ok       { color:#16a34a; font-weight:500; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  API Keys
# ═══════════════════════════════════════════════════════════════
def get_api_keys():
    rf_key = st.secrets.get("RAINFOREST_API_KEY", "") if hasattr(st, "secrets") else ""
    ka_key = st.secrets.get("KEEPA_API_KEY", "") if hasattr(st, "secrets") else ""

    with st.sidebar:
        st.markdown("### 🔑 API Keys")
        st.caption("已在 secrets 中配置则无需手动填写")
        rf_key = st.text_input("Rainforest API Key", value=rf_key, type="password")
        ka_key = st.text_input("Keepa API Key", value=ka_key, type="password")
        st.divider()
        st.markdown("### 📖 使用说明")
        st.markdown("""
1. 在上方输入 ASIN（10位字母数字）
2. 点击 **查询** 按钮
3. 数据约需 **3–8 秒** 加载

**数据来源**
- 🟢 Rainforest API：实时商品页
- 🟠 Keepa API：7天历史/90天统计

**分享**：部署到 [Streamlit Cloud](https://share.streamlit.io)，生成公开链接
        """)
    return rf_key, ka_key


# ═══════════════════════════════════════════════════════════════
#  缓存 API 调用（相同 ASIN 5分钟内不重复请求）
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def load_data(asin: str, rf_key: str, ka_key: str):
    errors = {}

    # Rainforest: 商品 + 竞对
    product, competitors = {}, []
    try:
        product = api.fetch_product(asin, rf_key)
        if product.get("brand"):
            search_term = f"{product['brand']} {product.get('bsr_category', 'product')}"
            try:
                competitors = api.fetch_competitors(search_term, rf_key, asin)
            except Exception as e:
                errors["competitors"] = str(e)
    except Exception as e:
        errors["rainforest"] = str(e)

    # Keepa: 历史趋势
    keepa = {}
    try:
        keepa = api.fetch_keepa(asin, ka_key)
    except Exception as e:
        errors["keepa"] = str(e)

    # 关键词排名
    kw_data = []
    try:
        title = product.get("title", "")
        brand = product.get("brand", "")
        if title:
            keywords = api.extract_keywords(title, brand)
            comp_asins = [c["asin"] for c in competitors if c.get("asin")]
            kw_data = api.fetch_keyword_rankings(asin, keywords, comp_asins, rf_key)
    except Exception as e:
        errors["keywords"] = str(e)

    # Listing 优化评分
    listing = {}
    try:
        comp_prices = [c["price"] for c in competitors if c.get("price")]
        listing = api.generate_listing_score(product, comp_prices)
    except Exception as e:
        errors["listing"] = str(e)

    return product, keepa, competitors, kw_data, listing, errors


# ═══════════════════════════════════════════════════════════════
#  图表工具函数
# ═══════════════════════════════════════════════════════════════
def last_7_days_labels():
    today = datetime.today()
    return [(today - timedelta(days=6 - i)).strftime("%-m/%-d") for i in range(7)]


def trend_chart(values: list, labels: list, title: str, color: str,
                y_format: str = "${:.2f}", reverse_color: bool = False):
    """Plotly 折线趋势图，None 值显示断点"""
    has_data = any(v is not None for v in values)

    if not has_data:
        fig = go.Figure()
        fig.add_annotation(text="暂无历史数据", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=13, color="#94a3b8"))
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=labels, y=values,
            mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline"),
            marker=dict(size=6, color=color,
                        line=dict(width=2, color="white")),
            connectgaps=False,
            hovertemplate="%{x}<br>" + title + ": " +
                          ("%{y:,.0f}" if "BSR" in title else "$%{y:.2f}") +
                          "<extra></extra>",
        ))

        clean = [v for v in values if v is not None]
        if len(clean) >= 2:
            pct = (clean[-1] - clean[0]) / clean[0] * 100
            if reverse_color:
                arrow = "▲ 排名提升" if pct < 0 else "▼ 排名下降"
                arrow_color = "#22c55e" if pct < 0 else "#ef4444"
            else:
                arrow = f"↑ +{abs(pct):.1f}%" if pct > 0 else f"↓ {abs(pct):.1f}%"
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
    """90天价格位置仪表盘"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current or 0,
        delta={"reference": p_avg, "valueformat": ".2f",
               "prefix": "均价Delta$", "increasing": {"color": "#ef4444"},
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


# ═══════════════════════════════════════════════════════════════
#  主界面渲染
# ═══════════════════════════════════════════════════════════════
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
            stars = "⭐" * int(round(rating))
            meta_parts.append(f"{stars} {rating}")
        if reviews:
            meta_parts.append(f"{reviews:,} 条评论")
        if product.get("variant_count"):
            meta_parts.append(f"{product['variant_count']} 个变体")
        if product.get("img_count"):
            meta_parts.append(f"{product['img_count']} 张图片")
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
            delta = f"较90日低点 +${price - p_min:.2f}"
        st.metric("💰 当前价格", f"${price:.2f}" if price else "—", delta=delta)

    with c2:
        bsr_cat = (product.get("bsr_category") or "")[:18]
        st.metric("📊 BSR 排名", f"#{bsr:,}" if bsr else "—",
                  delta=bsr_cat or None)

    with c3:
        st.metric("⭐ 综合评分", f"{rating} / 5.0" if rating else "—",
                  delta=f"{reviews:,} 条评论" if reviews else None)

    with c4:
        st.metric("📦 月销量估算", f"~{monthly:,} 件" if monthly else "—",
                  delta="来源：Keepa")

    with c5:
        avg = keepa.get("price_90d_avg")
        st.metric("📈 90日均价", f"${avg:.2f}" if avg else "—",
                  delta=f"区间 ${p_min:.2f}–${p_max:.2f}" if p_min and p_max else None)


def render_trends(keepa):
    price_7d = keepa.get("price_7d", [None] * 7)
    bsr_7d = keepa.get("bsr_7d", [None] * 7)
    labels = last_7_days_labels()

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.plotly_chart(
                trend_chart(price_7d, labels, "7天价格趋势", "#6366f1"),
                use_container_width=True, config={"displayModeBar": False},
            )
    with col2:
        with st.container(border=True):
            st.plotly_chart(
                trend_chart(bsr_7d, labels, "7天 BSR 趋势（主类目）",
                            "#f59e0b", reverse_color=True),
                use_container_width=True, config={"displayModeBar": False},
            )

    with st.expander("📋 7天逐日明细", expanded=False):
        rows = []
        for i, day in enumerate(labels):
            p = price_7d[i]
            b = bsr_7d[i]
            rows.append({
                "日期": day,
                "价格": f"${p:.2f}" if p else "—",
                "BSR（主类目）": f"#{b:,}" if b else "—",
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def render_price_stats(keepa, product):
    p_min = keepa.get("price_90d_min")
    p_avg = keepa.get("price_90d_avg")
    p_max = keepa.get("price_90d_max")
    current = product.get("current_price") or keepa.get("current_price")

    if not (p_min and p_avg and p_max):
        return

    with st.container(border=True):
        st.markdown("**📊 90天价格区间**")
        col_gauge, col_stat = st.columns([3, 2])
        with col_gauge:
            st.plotly_chart(
                price_range_gauge(current, p_min, p_avg, p_max),
                use_container_width=True, config={"displayModeBar": False},
            )
        with col_stat:
            st.markdown("")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("🟢 最低", f"${p_min:.2f}")
            mc2.metric("🟡 均价", f"${p_avg:.2f}")
            mc3.metric("🔴 最高", f"${p_max:.2f}")

            if current and p_min and p_max:
                pct = (current - p_min) / (p_max - p_min) * 100 if p_max != p_min else 50
                st.progress(int(min(100, max(0, pct))),
                            text=f"当前价格处于90日区间 **{pct:.0f}%** 位置")


def render_bsr_breakdown(product):
    all_bsr = product.get("all_bsr") or []
    if not all_bsr:
        return
    with st.container(border=True):
        st.markdown("**🏆 各类目 BSR 排名**")
        rows = [{'类目': b["category"], '排名': f"#{b['rank']:,}"} for b in all_bsr]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def render_bullets(product):
    bullets = product.get("feature_bullets") or []
    if not bullets:
        return
    with st.expander("✨ 核心卖点（Feature Bullets）", expanded=True):
        for b in bullets:
            st.markdown(f"- {b}")


def render_competitors(competitors, my_price):
    if not competitors:
        return

    st.markdown("### 🥊 竞对 ASIN 对比")
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
                    color = "🟢" if diff > 0 else "🔴"
                    diff_str = f"{color} {'+' if diff > 0 else ''}{diff:.2f}"
                    st.metric("价格", f"${price:.2f}", delta=diff_str)
                else:
                    st.metric("价格", "—")

                rating = c.get("rating")
                reviews = c.get("review_count")
                st.caption(
                    f"⭐ {rating or '—'}  ·  {f'{reviews:,}' if reviews else '—'} 评"
                )
                st.caption((c.get("title") or "")[:50] + "…")

    with st.expander("📋 竞对详细对比表", expanded=False):
        rows = []
        if my_price:
            rows.append({
                "ASIN": f"**{st.session_state.get('asin', '—')}（我的）**",
                "价格": f"${my_price:.2f}",
                "评分": "—", "评论数": "—", "Prime": "—"
            })
        for c in competitors:
            p = c.get("price")
            rows.append({
                "ASIN": c.get("asin", ""),
                "价格": f"${p:.2f}" if p else "—",
                "评分": c.get("rating") or "—",
                "评论数": f"{c['review_count']:,}" if c.get("review_count") else "—",
                "Prime": "✅" if c.get("is_prime") else "❌",
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def render_keywords(asin, kw_data, competitors):
    """关键词排名模块"""
    if not kw_data:
        return

    st.markdown("### 🔍 关键词排名分析")

    comp_asins = [c["asin"] for c in (competitors or []) if c.get("asin")]

    # 汇总表
    summary_rows = []
    for kw in kw_data:
        row = {
            "关键词": kw["keyword"],
            "我的排名": f"#{kw['my_rank']}" if kw.get("my_rank") else "未入榜(>40)",
        }
        for ca in comp_asins[:3]:
            cr = (kw.get("comp_ranks") or {}).get(ca)
            row[f"竞对 {ca[:10]}"] = f"#{cr}" if cr else "未入榜"
        if kw.get("error"):
            row["备注"] = "查询失败"
        summary_rows.append(row)

    with st.container(border=True):
        st.markdown("关键词排名概览")
        st.dataframe(pd.DataFrame(summary_rows), hide_index=True, use_container_width=True)

    # 每个关键词详细 Top5 搜索结果
    with st.expander("📋 各关键词 Top5 搜索结果", expanded=False):
        for kw in kw_data:
            st.markdown(f"🔑 {kw['keyword']}")
            my_rank = kw.get("my_rank")
            rank_str = f"第 {my_rank} 位" if my_rank else "未入前40"
            rank_color = "#16a34a" if my_rank and my_rank <= 10 else (
                "#d97706" if my_rank and my_rank <= 20 else "#dc2626"
            )
            st.markdown(
                f"<span style='color:{rank_color};font-weight:600'>我的排名：{rank_str}</span>",
                unsafe_allow_html=True,
            )
            top5 = kw.get("top5") or []
            if top5:
                t5_rows = []
                for idx, item in enumerate(top5):
                    is_me = item.get("asin") == asin
                    is_comp = item.get("asin") in comp_asins
                    tag = " 🟣我" if is_me else (" 🔴竞" if is_comp else "")
                    t5_rows.append({
                        "位置": f"#{idx + 1}",
                        "ASIN": f"{item.get('asin', '')}{tag}",
                        "标题": (item.get("title") or "")[:55],
                        "价格": f"${item['price']:.2f}" if item.get("price") else "—",
                    })
                st.dataframe(pd.DataFrame(t5_rows), hide_index=True, use_container_width=True)
            st.markdown("---")


def render_listing_score(listing):
    """Listing 优化建议模块"""
    if not listing:
        return

    score = listing.get("score", 0)
    suggestions = listing.get("suggestions") or []

    st.markdown("### 📝 Listing 优化评分")

    col_score, col_detail = st.columns([1, 3])
    with col_score:
        with st.container(border=True):
            if score >= 80:
                score_color = "#16a34a"
                score_label = "优秀"
            elif score >= 60:
                score_color = "#d97706"
                score_label = "待优化"
            else:
                score_color = "#dc2626"
                score_label = "需立即改善"

            st.markdown(
                f"""
                <div style="text-align:center;padding:12px 0">
                    <div style="font-size:48px;font-weight:800;color:{score_color}">{score}</div>
                    <div style="font-size:13px;color:{score_color};font-weight:600">{score_label}</div>
                    <div style="font-size:11px;color:#94a3b8;margin-top:4px">满分 100</div>
                    <div class="score-bar-wrap" style="margin-top:10px">
                        <div class="score-bar" style="width:{score}%;background:{score_color}"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            counts = {}
            for s in suggestions:
                p = s.get("priority", "low")
                counts[p] = counts.get(p, 0) + 1
            if counts.get("critical"):
                st.markdown(f"🔴 **{counts['critical']}** 项严重问题")
            if counts.get("high"):
                st.markdown(f"🟠 **{counts['high']}** 项高优先级")
            if counts.get("medium"):
                st.markdown(f"🟡 **{counts['medium']}** 项中优先级")
            if counts.get("ok"):
                st.markdown(f"🟢 **{counts['ok']}** 项已达标")

    with col_detail:
        with st.container(border=True):
            st.markdown("优化建议清单")
            priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "ok": 4}
            sorted_suggestions = sorted(
                suggestions, key=lambda x: priority_order.get(x.get("priority", "low"), 3)
            )
            for s in sorted_suggestions:
                p = s.get("priority", "low")
                icon_map = {
                    "critical": "🔴", "high": "🟠",
                    "medium": "🟡", "low": "🔵", "ok": "🟢"
                }
                icon = icon_map.get(p, "⚪")
                area = s.get("area", "")
                issue = s.get("issue", "")
                action = s.get("action", "")
                st.markdown(
                    f"{icon} **{area}** — {issue}  \n"
                    f"<span style='color:#64748b;font-size:12px'>建议：{action}</span>",
                    unsafe_allow_html=True,
                )
            if not sorted_suggestions:
                st.success("🎉 Listing 各项指标均达标！")


def render_error_banner(errors):
    if not errors:
        return
    with st.expander("⚠️ 部分数据源出现错误", expanded=True):
        for src, msg in errors.items():
            st.error(f"**{src}**: {msg}")


# ═══════════════════════════════════════════════════════════════
#  主程序入口
# ═══════════════════════════════════════════════════════════════
def main():
    rf_key, ka_key = get_api_keys()

    st.markdown(
        "<h2 style='margin-bottom:4px'>📦 Amazon ASIN Dashboard</h2>"
        "<p style='color:#64748b;font-size:14px;margin-bottom:16px'>"
        "输入任意 Amazon US ASIN，即时获取价格趋势、BSR排名、竞对分析、关键词排名、Listing优化</p>",
        unsafe_allow_html=True,
    )

    col_input, col_btn, col_spacer = st.columns([3, 1, 4])
    with col_input:
        asin_input = st.text_input(
            "ASIN",
            placeholder="B0D54LVZK5",
            max_chars=10,
            label_visibility="collapsed",
        ).strip().upper()
    with col_btn:
        search = st.button("🔍 查询", type="primary", use_container_width=True)

    st.markdown(
        "<p style='font-size:12px;color:#94a3b8'>示例：</p>",
        unsafe_allow_html=True,
    )
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
            <div style="font-size:48px">📦</div>
            <div style="font-size:18px;margin-top:12px;color:#64748b;font-weight:600">
                输入 ASIN 开始查询
            </div>
            <div style="font-size:13px;margin-top:8px">
                支持所有 Amazon.com 在售商品，数据实时拉取
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    if search and asin_input:
        st.session_state["last_asin"] = asin_input
    asin = st.session_state.get("last_asin", asin_input)

    if not asin or len(asin) != 10:
        st.warning("⚠️ ASIN 必须是10位字母数字，例如 B0D54LVZK5")
        return

    if not rf_key or not ka_key:
        st.error("❌ 请在左侧 Sidebar 填写 API Keys，或在 secrets.toml 中配置")
        return

    st.session_state["asin"] = asin

    with st.spinner(f"⏳ 正在查询 {asin}，同步调用 Rainforest + Keepa API…"):
        product, keepa, competitors, kw_data, listing, errors = load_data(asin, rf_key, ka_key)

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

    render_keywords(asin, kw_data, competitors)

    render_listing_score(listing)

    st.markdown("---")
    fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tokens = keepa.get("tokens_left")
    st.caption(
        f"数据更新时间：{fetch_time}  ·  ASIN: `{asin}`"
        + (f"  ·  Keepa 剩余 Tokens：{tokens:,}" if tokens else "")
    )


if __name__ == "__main__":
    main()
