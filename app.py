import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(
    page_title="Yurise.ai · Amazon卖家运营工具",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background:#0f172a !important; }
[data-testid="stHeader"]  { display:none !important; }
[data-testid="stToolbar"] { display:none !important; }
footer { display:none !important; }
.block-container { padding:0 !important; max-width:100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background:rgba(10,17,35,0.98) !important;
  border-right:1px solid rgba(71,85,105,0.35) !important;
  min-width:190px !important; max-width:190px !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { padding:0; }
[data-testid="stSidebarContent"] { padding:0 !important; }

/* ── Module section header ── */
.mod-header {
  display:flex; align-items:center; justify-content:space-between;
  background:rgba(30,41,59,0.55);
  border-left:3px solid #3b82f6;
  border-radius:0 10px 10px 0;
  padding:10px 16px; margin-bottom:2px;
}
.mod-title {
  font-size:13px; font-weight:700; color:#f1f5f9;
  background:linear-gradient(90deg,#60a5fa,#a78bfa);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  letter-spacing:0.2px;
}
.mod-score { font-size:12px; font-weight:600; color:#94a3b8; }

/* ── inputs ── */
[data-testid="stTextInput"] input {
  background:#1e293b !important; color:#e2e8f0 !important;
  border:1px solid #475569 !important; border-radius:8px !important;
}
[data-testid="stSelectbox"] > div > div {
  background:#1e293b !important; color:#e2e8f0 !important;
  border:1px solid #475569 !important; border-radius:8px !important;
}
[data-testid="stRadio"] label { color:#cbd5e1 !important; }
button[kind="primary"], .stButton > button {
  background:#3b82f6 !important; color:white !important;
  border:none !important; border-radius:8px !important; font-weight:600 !important;
}
.stButton > button:hover { background:#2563eb !important; }

/* ── expanders ── */
[data-testid="stExpander"] {
  background:rgba(30,41,59,0.35) !important;
  border:1px solid rgba(71,85,105,0.5) !important; border-radius:0 0 12px 12px !important;
  border-top:none !important;
}
[data-testid="stExpander"] summary { color:#94a3b8 !important; font-weight:500 !important; font-size:12px !important; }
[data-testid="stExpander"] summary:hover { color:#93c5fd !important; }

/* ── tabs ── */
[data-testid="stTabs"] [role="tablist"] { background:#1e293b; border-radius:8px; padding:2px; border:1px solid #334155; }
[data-testid="stTabs"] [role="tab"] { color:#94a3b8 !important; border-radius:6px; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { background:#3b82f6 !important; color:white !important; }

/* ── metrics ── */
[data-testid="metric-container"] { background:rgba(30,41,59,0.5); border:1px solid rgba(71,85,105,0.6); border-radius:8px; padding:12px; }
[data-testid="stMetricLabel"] { color:#94a3b8 !important; font-size:11px !important; }
[data-testid="stMetricValue"] { color:#f1f5f9 !important; font-size:20px !important; }

/* ── dataframe ── */
[data-testid="stDataFrame"] { background:#1e293b !important; border-radius:8px; overflow:hidden; }

/* ── plotly ── */
.js-plotly-plot .plotly .bg { fill:#0f172a !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#1e293b; }
::-webkit-scrollbar-thumb { background:#475569; border-radius:3px; }

/* ── cards ── */
.diag-topbar { background:rgba(15,23,42,0.97); border-bottom:1px solid rgba(71,85,105,0.6); padding:10px 24px; }
.diag-card   { background:rgba(30,41,59,0.4); border:1px solid rgba(71,85,105,0.6); border-radius:12px; padding:16px; }
.diag-label  { font-size:11px; color:#94a3b8; margin-bottom:3px; }
.diag-val    { font-size:18px; font-weight:700; color:#f1f5f9; }
.diag-sub    { font-size:11px; color:#64748b; margin-top:2px; }
.diag-highlight { border-color:rgba(245,158,11,0.5) !important; background:rgba(245,158,11,0.06) !important; }

/* ── badges ── */
.badge { display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:600; border-width:1px; border-style:solid; }
.badge-excellent { background:rgba(16,185,129,0.15); color:#34d399; border-color:rgba(52,211,153,0.4); }
.badge-good      { background:rgba(59,130,246,0.15); color:#60a5fa; border-color:rgba(96,165,250,0.4); }
.badge-normal    { background:rgba(245,158,11,0.15); color:#fbbf24; border-color:rgba(251,191,36,0.4); }
.badge-bad       { background:rgba(239,68,68,0.15);  color:#f87171; border-color:rgba(248,113,113,0.4); }
.badge-opp       { background:rgba(59,130,246,0.15); color:#60a5fa; border-color:rgba(96,165,250,0.4); }
.badge-risk      { background:rgba(239,68,68,0.15);  color:#f87171; border-color:rgba(248,113,113,0.4); }
.badge-stable    { background:rgba(100,116,139,0.2); color:#94a3b8; border-color:rgba(148,163,184,0.3); }
.badge-warn      { background:rgba(245,158,11,0.15); color:#fbbf24; border-color:rgba(251,191,36,0.4); }
.badge-abn       { background:rgba(239,68,68,0.15);  color:#f87171; border-color:rgba(248,113,113,0.4); }

/* ── judgment boxes ── */
.judge-warn { background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.3); border-radius:8px; padding:10px 14px; font-size:12px; color:#fcd34d; margin:10px 0; }
.judge-info { background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.3); border-radius:8px; padding:10px 14px; font-size:12px; color:#93c5fd; margin:10px 0; }

/* ── adv/dis cards ── */
.adv-card { background:rgba(16,185,129,0.06); border:1px solid rgba(52,211,153,0.25); border-radius:8px; padding:12px; }
.dis-card { background:rgba(239,68,68,0.06); border:1px solid rgba(248,113,113,0.25); border-radius:8px; padding:12px; }
.risk-box { background:rgba(245,158,11,0.06); border:1px solid rgba(245,158,11,0.25); border-radius:8px; padding:10px 14px; font-size:12px; color:#fcd34d; }
.prio-box { background:rgba(59,130,246,0.06); border:1px solid rgba(59,130,246,0.25); border-radius:8px; padding:10px 14px; font-size:12px; color:#93c5fd; }

/* ── action rows ── */
.action-row { display:flex; align-items:flex-start; gap:8px; margin-bottom:6px; }
.action-icon { color:#60a5fa; margin-top:1px; flex-shrink:0; }

/* ── tables ── */
.tbl-wrapper { overflow-x:auto; border-radius:8px; border:1px solid rgba(71,85,105,0.5); }
table.dtbl { width:100%; border-collapse:collapse; font-size:12px; }
table.dtbl th { background:rgba(51,65,85,0.6); color:#94a3b8; padding:8px 12px; text-align:left; font-weight:500; border-bottom:1px solid rgba(71,85,105,0.5); white-space:nowrap; }
table.dtbl td { padding:8px 12px; color:#cbd5e1; border-bottom:1px solid rgba(71,85,105,0.35); }
table.dtbl tr:hover td { background:rgba(51,65,85,0.3); }
.red-val { color:#f87171; font-weight:700; }
.green-val { color:#34d399; font-weight:700; }
.amber-val { color:#fbbf24; font-weight:700; }
.blue-val { color:#60a5fa; }

/* ── plan cards ── */
.plan-card { border-radius:12px; padding:20px; }
.plan-a { background:rgba(59,130,246,0.06); border:1px solid rgba(96,165,250,0.3); }
.plan-b { background:rgba(16,185,129,0.06); border:1px solid rgba(52,211,153,0.3); }
.p0 { background:rgba(239,68,68,0.12); color:#f87171; border:1px solid rgba(248,113,113,0.3); padding:2px 7px; border-radius:4px; font-size:11px; font-weight:700; }
.p1 { background:rgba(245,158,11,0.12); color:#fbbf24; border:1px solid rgba(251,191,36,0.3); padding:2px 7px; border-radius:4px; font-size:11px; font-weight:700; }
.p2 { background:rgba(59,130,246,0.12); color:#60a5fa; border:1px solid rgba(96,165,250,0.3); padding:2px 7px; border-radius:4px; font-size:11px; font-weight:700; }

/* ── p-card ── */
.p-card { background:rgba(30,41,59,0.4); border-radius:8px; padding:10px; }

/* ── sidebar nav ── */
.nav-logo {
  padding:18px 16px 12px 16px;
  border-bottom:1px solid rgba(71,85,105,0.3);
  margin-bottom:8px;
}
.nav-logo-name {
  font-size:15px; font-weight:800; color:white; letter-spacing:-0.3px;
  background:linear-gradient(90deg,#60a5fa,#a78bfa);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.nav-logo-sub { font-size:10px; color:#475569; margin-top:2px; }
.nav-section { padding:4px 8px; margin:0 8px; }
.nav-section-label { font-size:10px; color:#475569; font-weight:600; letter-spacing:0.8px; text-transform:uppercase; padding:6px 8px 4px 8px; }
.nav-item {
  display:flex; align-items:center; gap:8px;
  padding:7px 10px; border-radius:8px; margin-bottom:2px;
  cursor:pointer; text-decoration:none;
  color:#94a3b8; font-size:12px; font-weight:500;
  transition:all 0.15s;
}
.nav-item:hover { background:rgba(59,130,246,0.12); color:#93c5fd; text-decoration:none; }
.nav-item-icon { font-size:14px; flex-shrink:0; }
.nav-score-pill {
  margin-left:auto; font-size:10px; font-weight:700;
  padding:1px 6px; border-radius:10px;
  background:rgba(51,65,85,0.6); color:#64748b;
}
.nav-divider { height:1px; background:rgba(71,85,105,0.25); margin:8px 16px; }

/* ── section anchor ── */
.sec-anchor { scroll-margin-top:10px; }

/* ── api fn code display ── */
.api-fn-wrap { display:flex; flex-wrap:wrap; gap:6px; margin-top:10px; padding-top:10px; border-top:1px solid rgba(71,85,105,0.4); }
.api-fn {
  font-family:monospace; font-size:10px; color:#60a5fa;
  background:rgba(59,130,246,0.1); border:1px solid rgba(96,165,250,0.25);
  padding:3px 9px; border-radius:5px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────────────────────────
MOCK = {
    "product": {
        "asin": "B0D54LVZK5",
        "title": "SoundMax Pro X1 Portable Bluetooth Speaker, 360° Surround Sound, 24H Battery, IPX7 Waterproof, Dual Pairing, USB-C Charging",
        "brand": "SoundMax",
        "category": "Bluetooth Speakers",
        "price": 45.99, "rating": 4.2, "reviewCount": 1247,
        "inventoryStatus": "In Stock", "buyBoxStatus": "Won", "buyBoxWinRate": 94,
        "listingQualityScore": 72, "bsr": 247,
        "features": ["IPX7 Waterproof","24H Battery","360° Sound","Dual Pairing","USB-C"],
    },
    "scores": {"category":9,"brand":7,"competition":13,"keywords":14,"ads":14,"listing":10,"total":67},
    "scoreMeta": [
        {"key":"category",    "label":"品类表现",     "max":15},
        {"key":"brand",       "label":"品牌表现",     "max":10},
        {"key":"competition", "label":"竞品竞争力",   "max":20},
        {"key":"keywords",    "label":"关键词能力",   "max":20},
        {"key":"ads",         "label":"广告效率",     "max":20},
        {"key":"listing",     "label":"Listing&评论", "max":15},
    ],
    "trend_dates":   ["6/24","6/25","6/26","6/27","6/28","6/29","6/30"],
    "our_sales":     [42, 38, 45, 41, 37, 34, 33],
    "cat_avg":       [35, 36, 38, 37, 38, 37, 39],
    "top10_avg":     [180,185,190,188,192,189,195],
    "cat_share":     [1.9,1.8,2.0,1.8,1.7,1.5,1.5],
    "top_brands": [
        {"brand":"Anker",    "share":18.2},
        {"brand":"JBL",      "share":14.5},
        {"brand":"Sony",     "share":9.8},
        {"brand":"Bose",     "share":8.1},
        {"brand":"Tribit",   "share":6.4},
        {"brand":"SoundMax", "share":4.2},
    ],
    "brand_trend": [
        {"date":"6/24","brandIdx":100,"catIdx":100},
        {"date":"6/25","brandIdx":93, "catIdx":103},
        {"date":"6/26","brandIdx":106,"catIdx":106},
        {"date":"6/27","brandIdx":98, "catIdx":103},
        {"date":"6/28","brandIdx":90, "catIdx":105},
        {"date":"6/29","brandIdx":82, "catIdx":104},
        {"date":"6/30","brandIdx":80, "catIdx":107},
    ],
    "competitors": [
        {"asin":"B0D54LVZK5","brand":"SoundMax","price":45.99,"discount":8, "rating":4.2,"reviews":1247,  "sales":980,  "budget":"$2,847","lscore":72,"bsr":247, "ours":True},
        {"asin":"B08N5WRWNW","brand":"Anker",   "price":35.99,"discount":0, "rating":4.6,"reviews":15420, "sales":2840, "budget":"$8,200","lscore":91,"bsr":12,  "ours":False},
        {"asin":"B07FZ8S74R","brand":"JBL",     "price":59.95,"discount":15,"rating":4.5,"reviews":8520,  "sales":1650, "budget":"$5,400","lscore":88,"bsr":28,  "ours":False},
        {"asin":"B09B8ZCPKQ","brand":"Sony",    "price":39.99,"discount":10,"rating":4.3,"reviews":6240,  "sales":1240, "budget":"$3,800","lscore":85,"bsr":45,  "ours":False},
        {"asin":"B08CXVYZ2J","brand":"Tribit",  "price":39.99,"discount":5, "rating":4.4,"reviews":12180, "sales":1890, "budget":"$4,200","lscore":86,"bsr":22,  "ours":False},
        {"asin":"B09G9WV99B","brand":"Bose",    "price":89.00,"discount":0, "rating":4.6,"reviews":4120,  "sales":820,  "budget":"$2,100","lscore":93,"bsr":68,  "ours":False},
    ],
    "keywords": [
        {"kw":"bluetooth speaker",          "vol":450000,"trend":"↑","org":18,"spn":5, "chg":-3,"cov":5,"opp":82,"status":"opp"},
        {"kw":"portable bluetooth speaker", "vol":180000,"trend":"→","org":32,"spn":8, "chg":-2,"cov":5,"opp":74,"status":"opp"},
        {"kw":"small bluetooth speaker",    "vol":85000, "trend":"↑","org":12,"spn":3, "chg": 2,"cov":4,"opp":88,"status":"good"},
        {"kw":"waterproof bluetooth speaker","vol":120000,"trend":"↑","org":45,"spn":15,"chg":-5,"cov":5,"opp":65,"status":"risk"},
        {"kw":"outdoor bluetooth speaker",  "vol":65000, "trend":"↑","org":22,"spn":6, "chg": 1,"cov":3,"opp":79,"status":"stable"},
    ],
    "ads_summary": {"spend":2847,"impressions":145000,"clicks":3480,"ctr":2.4,"cvr":8.97,"cpc":0.82,"conv":312,"acos":28.5,"roas":3.51},
    "campaigns": [
        {"name":"SP - Exact - Core KWs","spend":1240,"impr":68000,"clicks":1680,"ctr":2.47,"cvr":9.4, "acos":24.8,"roas":4.03,"health":"good"},
        {"name":"SP - Broad - Discovery","spend":890, "impr":52000,"clicks":1140,"ctr":2.19,"cvr":7.63,"acos":32.4,"roas":3.09,"health":"warn"},
        {"name":"SP - Auto Campaign",   "spend":717, "impr":25000,"clicks":660, "ctr":2.64,"cvr":10.15,"acos":33.8,"roas":2.96,"health":"warn"},
    ],
    "ad_kws": [
        {"kw":"bluetooth speaker",       "spend":420,"clicks":510,"ctr":3.1,"cpc":0.82,"conv":48,"cvr":9.41, "acos":27.7,"status":"stable"},
        {"kw":"portable speaker",        "spend":285,"clicks":340,"ctr":2.5,"cpc":0.84,"conv":28,"cvr":8.24, "acos":32.1,"status":"warn"},
        {"kw":"small bluetooth speaker", "spend":198,"clicks":245,"ctr":3.8,"cpc":0.81,"conv":31,"cvr":12.65,"acos":20.1,"status":"opp"},
        {"kw":"waterproof speaker",      "spend":312,"clicks":280,"ctr":1.9,"cpc":1.11,"conv":18,"cvr":6.43, "acos":54.9,"status":"abn"},
        {"kw":"outdoor speaker",         "spend":156,"clicks":198,"ctr":2.7,"cpc":0.79,"conv":22,"cvr":11.11,"acos":22.4,"status":"opp"},
        {"kw":"360 bluetooth speaker",   "spend":89, "clicks":112,"ctr":2.2,"cpc":0.79,"conv":8, "cvr":7.14, "acos":35.1,"status":"warn"},
        {"kw":"ipx7 speaker",            "spend":64, "clicks":78, "ctr":1.6,"cpc":0.82,"conv":4, "cvr":5.13, "acos":50.3,"status":"abn"},
    ],
}

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def status_of(score):
    if score >= 90: return "优秀"
    if score >= 75: return "较好"
    if score >= 60: return "正常"
    return "异常"

def badge_html(s):
    cls_map = {
        "优秀":"badge-excellent","较好":"badge-good","正常":"badge-normal","异常":"badge-bad",
        "opp":"badge-opp","good":"badge-excellent","stable":"badge-stable",
        "risk":"badge-risk","warn":"badge-warn","abn":"badge-abn",
    }
    label_map = {
        "优秀":"优秀","较好":"较好","正常":"正常","异常":"异常",
        "opp":"机会","good":"良好","stable":"稳定","risk":"风险","warn":"待优化","abn":"异常",
    }
    cls = cls_map.get(s, "badge-stable")
    label = label_map.get(s, s)
    return f'<span class="badge {cls}"><span style="width:6px;height:6px;border-radius:50%;display:inline-block;background:currentColor;opacity:.7"></span>{label}</span>'

def score_color(pct):
    if pct >= 90: return "#34d399"
    if pct >= 75: return "#60a5fa"
    if pct >= 60: return "#fbbf24"
    return "#f87171"

def mod_header(icon, title, badge_key, score, max_score):
    """Styled module section header with background + highlighted title."""
    sc_pct = round(score / max_score * 100)
    sc_clr = score_color(sc_pct)
    badge = badge_html(badge_key)
    return f"""
    <div class="mod-header">
      <div style="display:flex;align-items:center;gap:10px">
        <span style="font-size:16px">{icon}</span>
        <span class="mod-title">{title}</span>
        {badge}
      </div>
      <div style="display:flex;align-items:center;gap:8px">
        <span class="mod-score">{score}/{max_score}歎</span>
        <div style="width:60px;height:4px;background:#1e293b;border-radius:2px;overflow:hidden">
          <div style="height:100%;width:{sc_pct}%;background:{sc_clr};border-radius:2px"></div>
        </div>
        <span style="font-size:11px;font-weight:700;color:{sc_clr}">{sc_pct}%</span>
      </div>
    </div>"""

def action_list(actions):
    rows = "".join(
        f'<div class="action-row"><span class="action-icon">→</span>'
        f'<span style="font-size:12px;color:#cbd5e1">{a}</span></div>'
        for a in actions
    )
    return f'<div style="margin-top:8px">{rows}</div>'

def judgment(text, t="warn"):
    cls = "judge-warn" if t == "warn" else "judge-info"
    icon = "⚠" if t == "warn" else "ℹ"
    return f'<div class="{cls}">{icon}&nbsp; {text}</div>'

def plotly_cfg():
    return dict(displayModeBar=False, responsive=True)

def dark_layout(**kwargs):
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.5)",
        font=dict(color="#94a3b8", size=11),
        margin=dict(l=10,r=10,t=30,b=10),
        xaxis=dict(gridcolor="#1e293b", linecolor="#334155", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#1e293b", linecolor="#334155", tickfont=dict(size=10)),
        legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#1e293b", bordercolor="#334155", font=dict(color="#e2e8f0", size=11)),
    )
    base.update(kwargs)
    return base

# ─────────────────────────────────────────────────────────────
# SIDEBAR  —  Elevator Navigation
# ─────────────────────────────────────────────────────────────

def render_sidebar():
    scores = MOCK["scores"]
    nav_items = [
        ("🏠", "概览总览",   "sec-overview",   scores["total"],       100),
        ("📊", "品类分析",   "sec-category",   scores["category"],    15),
        ("🏆", "品牌分析",   "sec-brand",      scores["brand"],       10),
        ("🎯", "竞品分析",   "sec-competitor", scores["competition"], 20),
        ("🔍", "关键词分析", "sec-keywords",   scores["keywords"],    20),
        ("💰", "广告分析",   "sec-ads",        scores["ads"],         20),
        ("📋", "30天方案",   "sec-plan",       None,                  None),
    ]

    total = scores["total"]
    overall = status_of(total)
    c_map = {"优秀":"#34d399","较好":"#60a5fa","正常":"#fbbf24","异常":"#f87171"}
    ring_clr = c_map[overall]

    items_html = ""
    for icon, label, anchor, sc, mx in nav_items:
        pill = ""
        if sc is not None and mx is not None:
            pct = round(sc / mx * 100)
            clr = score_color(pct)
            pill = f'<span class="nav-score-pill" style="color:{clr};background:rgba(30,41,59,0.8)">{sc}/{mx}</span>'
        items_html += f"""
        <a class="nav-item" href="#{anchor}" style="text-decoration:none">
          <span class="nav-item-icon">{icon}</span>
          <span>{label}</span>
          {pill}
        </a>"""

    with st.sidebar:
        st.markdown(f"""
        <div class="nav-logo">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
            <div style="width:26px;height:26px;background:linear-gradient(135deg,#3b82f6,#7c3aed);border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:14px">🚀</div>
            <div>
              <div class="nav-logo-name">Yurise.ai</div>
              <div class="nav-logo-sub">Amazon卖家运营工具</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:8px;background:rgba(30,41,59,0.5);border:1px solid rgba(71,85,105,0.4);border-radius:8px;padding:8px 10px;margin-top:8px">
            <div style="text-align:center">
              <div style="font-size:22px;font-weight:800;color:{ring_clr};line-height:1">{total}</div>
              <div style="font-size:9px;color:#475569">/100</div>
            </div>
            <div style="flex:1">
              <div style="font-size:11px;color:#94a3b8;margin-bottom:4px">综合健康分</div>
              <div style="height:4px;background:#1e293b;border-radius:2px;overflow:hidden">
                <div style="height:100%;width:{total}%;background:{ring_clr};border-radius:2px"></div>
              </div>
              <div style="font-size:10px;color:{ring_clr};font-weight:600;margin-top:3px">{overall}</div>
            </div>
          </div>
        </div>
        <div class="nav-section-label">模块导航</div>
        {items_html}
        <div class="nav-divider"></div>
        <div style="padding:8px 18px;font-size:10px;color:#334155;line-height:1.6">
          模拟数据模式<br>可替换为真实 API
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TOP BAR
# ─────────────────────────────────────────────────────────────

def render_topbar():
    st.markdown("""
    <div class="diag-topbar" style="display:flex;align-items:center;justify-content:space-between">
      <div style="display:flex;align-items:center;gap:10px">
        <div style="width:22px;height:22px;background:linear-gradient(135deg,#3b82f6,#7c3aed);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:13px">🚀</div>
        <span style="font-size:15px;font-weight:800;background:linear-gradient(90deg,#60a5fa,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-0.3px">Yurise.ai</span>
        <span style="font-size:12px;color:#64748b">Amazon卖家运营工具</span>
      </div>
      <span style="font-size:11px;color:#64748b">
        <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#f59e0b;margin-right:5px"></span>
        模拟数据模式 · 可替换为真实 API 数据
      </span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# OVERVIEW
# ─────────────────────────────────────────────────────────────

def render_overview(asin):
    p = MOCK["product"]
    scores = MOCK["scores"]
    meta = MOCK["scoreMeta"]
    total = scores["total"]
    overall = status_of(total)
    color_map = {"优秀":"#34d399","较好":"#60a5fa","正常":"#fbbf24","异常":"#f87171"}
    ring_color = color_map[overall]

    st.markdown('<div id="sec-overview" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 24px 0 24px">', unsafe_allow_html=True)

    col_info, col_score = st.columns([7, 5])

    with col_info:
        st.markdown(f"""
        <div class="diag-card">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
            <span style="background:rgba(59,130,246,0.2);color:#60a5fa;border:1px solid rgba(96,165,250,0.4);padding:2px 8px;border-radius:4px;font-size:11px;font-family:monospace">{p['asin']}</span>
            <span style="font-size:11px;color:#64748b">{p['category']}</span>
          </div>
          <div style="font-size:13px;font-weight:600;color:white;line-height:1.5;margin-bottom:14px">{p['title']}</div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px">
            {''.join([
              f'<div class="p-card"><div class="diag-label">{l}</div><div style="font-size:13px;font-weight:600;color:{c}">{v}</div></div>'
              for l,v,c in [
                ("品牌",p["brand"],"#60a5fa"),
                ("价格",f"${p['price']}","white"),
                ("评分/评论",f"{p['rating']}★ / {p['reviewCount']:,}","#fbbf24"),
                ("BSR",f"#{p['bsr']}","#f87171"),
                ("库存",p["inventoryStatus"],"#34d399"),
                ("Buy Box",f"{p['buyBoxStatus']} ({p['buyBoxWinRate']}%)","white"),
                ("Listing分",f"{p['listingQualityScore']}/100","#fbbf24"),
                ("核心功能"," · ".join(p["features"][:2]),"#94a3b8"),
              ]
            ])}
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_score:
        bars_html = ""
        for m in meta:
            sc = scores[m["key"]]
            mx = m["max"]
            pct = round(sc / mx * 100)
            bar_color = score_color(pct)
            bars_html += f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
              <div style="width:88px;font-size:10px;color:#94a3b8;text-align:right;flex-shrink:0">{m['label']}</div>
              <div style="flex:1;height:5px;background:#1e293b;border-radius:3px;overflow:hidden">
                <div style="height:100%;width:{pct}%;background:{bar_color};border-radius:3px"></div>
              </div>
              <div style="font-size:10px;color:{bar_color};font-weight:600;width:42px">{sc}/{mx}</div>
            </div>"""

        st.markdown(f"""
        <div class="diag-card">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
            <span style="font-size:13px;font-weight:600;color:white">健康评分</span>
            {badge_html(overall)}
          </div>
          <div style="display:flex;align-items:center;gap:16px;margin-bottom:12px">
            <div style="text-align:center;flex-shrink:0">
              <div style="font-size:36px;font-weight:800;color:{ring_color};line-height:1">{total}</div>
              <div style="font-size:10px;color:#64748b">/ 100</div>
            </div>
            <div style="flex:1">{bars_html}</div>
          </div>
          <div style="background:rgba(51,65,85,0.4);border:1px solid rgba(71,85,105,0.5);border-radius:8px;padding:10px;font-size:11px;color:#94a3b8">
            <span style="color:#e2e8f0">综合诊断：</span>该 ASIN 处于
            <span style="color:#fbbf24;font-weight:600">正常</span>水平，评论量不足是核心瓶颈，关键词自然流量有较大提升空间，广告存在浪费。
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    issues = [
        "评论量仅1,247，竞品均值超9,000，转化信任度严重不足",
        "Listing 质量分72分（满分100），图片和描述有优化空间",
        "BSR 连续7天下滑，当前 #247，需广告干预",
    ]
    opportunities = [
        "'bluetooth speaker'(45万搜量)自然排名#18，进入Top10可大幅提升有机流量",
        "'small bluetooth speaker'自然排名#12，广告ACOS仅20.1%，可放量",
        "类目需求整体健康增长，竞品无明显价格护城河",
    ]
    suggestions = [
        "30天内 Review 数量冲破2,000（Request a Review + Vine）",
        "暂停 ACOS>50% 的广告词，节省约$376/月",
        "开启 Sponsored Brands 视频广告，提升品牌认知",
    ]
    for col, title, icon, color, items in [
        (c1, "核心问题 Top 3", "⚠", "#f87171", issues),
        (c2, "核心机会 Top 3", "◎", "#60a5fa", opportunities),
        (c3, "建议动作 Top 3", "⚡", "#34d399", suggestions),
    ]:
        with col:
            rows = "".join(
                f'<div style="display:flex;gap:6px;margin-bottom:6px">'
                f'<span style="color:{color};font-weight:700;flex-shrink:0">{i+1}.</span>'
                f'<span style="font-size:11px;color:#cbd5e1">{item}</span></div>'
                for i,item in enumerate(items)
            )
            st.markdown(f"""
            <div class="diag-card">
              <div style="font-size:12px;font-weight:600;color:{color};margin-bottom:10px">{icon} {title}</div>
              {rows}
            </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MODULE 1 — CATEGORY
# ─────────────────────────────────────────────────────────────

def render_category():
    d = MOCK
    sc = MOCK["scores"]["category"]
    st.markdown('<div id="sec-category" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(mod_header("📊", "品类分析", "正常", sc, 15), unsafe_allow_html=True)
    with st.expander("展开详情", expanded=True):
        c1,c2,c3,c4,c5 = st.columns(5)
        cols_data = [
            (c1, "当日销量", "33", "件", "近7日均值38.6件", True),
            (c2, "类目均值", "37.1", "件", "Top100日均", False),
            (c3, "类目份额", "1.5%", "", "连续3日下滑", True),
            (c4, "BSR排名",  "#247", "", "7天跌36位", True),
            (c5, "Top10均值","191", "件", "差距×5.8倍", False),
        ]
        for col, label, val, unit, sub, hl in cols_data:
            with col:
                color = "#fbbf24" if hl else "white"
                hl_style = "border-color:rgba(245,158,11,0.5);background:rgba(245,158,11,0.05)" if hl else ""
                st.markdown(f"""
                <div class="diag-card" style="{hl_style}">
                  <div class="diag-label">{label}</div>
                  <div style="font-size:18px;font-weight:700;color:{color}">{val}<span style="font-size:11px;color:#94a3b8;margin-left:2px">{unit}</span></div>
                  <div class="diag-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d["trend_dates"], y=d["our_sales"], name="我方销量",
            line=dict(color="#60a5fa", width=2), fill="tozeroy",
            fillcolor="rgba(96,165,250,0.1)"))
        fig.add_trace(go.Scatter(x=d["trend_dates"], y=d["cat_avg"], name="类目均值",
            line=dict(color="#a78bfa", width=1.5, dash="dash")))
        fig.update_layout(dark_layout(title="7日销量趋势对比", height=200))
        st.plotly_chart(fig, use_container_width=True, config=plotly_cfg())

        brands = d["top_brands"]
        fig2 = go.Figure(go.Bar(
            x=[b["share"] for b in brands], y=[b["brand"] for b in brands],
            orientation="h",
            marker=dict(color=["#34d399" if b["brand"]=="SoundMax" else "#3b82f6" for b in brands]),
        ))
        fig2.update_layout(dark_layout(title="类目品牌份额分布 (%)", height=200, xaxis_title="市场份额 (%)"))
        st.plotly_chart(fig2, use_container_width=True, config=plotly_cfg())

        st.markdown(judgment("销量趋势7日连续下滑，当前份额1.5%低于类目均值；类目整体保持增长，品类需求健康。"), unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#94a3b8;margin-top:10px;margin-bottom:4px">建议动作</div>', unsafe_allow_html=True)
        st.markdown(action_list([
            "立即检查是否有差评或 Q&A 影响转化",
            "加强关键词广告投放，阻止 BSR 继续下滑",
            "考虑 Coupon 或 Prime Exclusive Discount 刺激转化",
        ]), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MODULE 2 — BRAND
# ─────────────────────────────────────────────────────────────

def render_brand():
    d = MOCK
    sc = MOCK["scores"]["brand"]
    st.markdown('<div id="sec-brand" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(mod_header("🏆", "品牌分析", "正常", sc, 10), unsafe_allow_html=True)
    with st.expander("展开详情", expanded=True):
        c1,c2,c3,c4 = st.columns(4)
        for col, label, val, sub, hl in [
            (c1,"品牌类目排名","#8","Top10品牌",False),
            (c2,"品牌市场份额","4.2%","过去7天",False),
            (c3,"本ASIN贡献度","42%","占品牌总销量",True),
            (c4,"品牌增长WoW","-3.2%","类目同期+1.4%",True),
        ]:
            with col:
                color = "#fbbf24" if hl else "white"
                hl_style = "border-color:rgba(245,158,11,0.5);background:rgba(245,158,11,0.05)" if hl else ""
                st.markdown(f"""
                <div class="diag-card" style="{hl_style}">
                  <div class="diag-label">{label}</div>
                  <div style="font-size:18px;font-weight:700;color:{color}">{val}</div>
                  <div class="diag-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        bt = d["brand_trend"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[r["date"] for r in bt], y=[r["brandIdx"] for r in bt], name="品牌指数",
            line=dict(color="#60a5fa", width=2), mode="lines+markers",
            marker=dict(size=4, color="#60a5fa")))
        fig.add_trace(go.Scatter(
            x=[r["date"] for r in bt], y=[r["catIdx"] for r in bt], name="类目指数",
            line=dict(color="#a78bfa", width=1.5, dash="dash"), mode="lines"))
        fig.add_hline(y=100, line=dict(color="#334155", dash="dot"), annotation_text="基准线")
        fig.update_layout(dark_layout(title="品牌 vs 类目趋势指数（基准=100）", height=200, yaxis_range=[78,115]))
        st.plotly_chart(fig, use_container_width=True, config=plotly_cfg())

        st.markdown(judgment("品牌整体在下滑（-3.2% WoW），而类目同期增长1.4%；本 ASIN 贡献品牌42%销量，品牌势能偏弱。"), unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#94a3b8;margin-top:10px;margin-bottom:4px">建议动作</div>', unsafe_allow_html=True)
        st.markdown(action_list([
            "检查品牌下其他 ASIN 是否存在 Review 问题拖累品牌整体",
            "考虑开启 Sponsored Brands 广告，强化品牌认知度",
            "评估是否需要推出新款 ASIN 补充产品线",
        ]), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MODULE 3 — COMPETITORS
# ─────────────────────────────────────────────────────────────

def render_competitors():
    sc = MOCK["scores"]["competition"]
    comps = MOCK["competitors"]
    st.markdown('<div id="sec-competitor" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(mod_header("🎯", "竞品分析", "正常", sc, 20), unsafe_allow_html=True)
    with st.expander("展开详情", expanded=True):
        rows_html = ""
        for c in comps:
            ours = c["ours"]
            prefix = '<span style="background:rgba(59,130,246,0.2);color:#60a5fa;border:1px solid rgba(96,165,250,0.4);padding:1px 6px;border-radius:3px;font-size:10px;margin-right:4px">我方</span>' if ours else ""
            rev_color = 'class="red-val"' if ours and c["reviews"]<3000 else ""
            rat_color = "green-val" if c["rating"]>=4.5 else ("amber-val" if c["rating"]>=4.0 else "red-val")
            ls_color  = "green-val" if c["lscore"]>=85 else ("amber-val" if c["lscore"]>=75 else "red-val")
            disc = f'<span class="green-val">-{c["discount"]}%</span>' if c["discount"]>0 else "—"
            row_style = ' style="background:rgba(59,130,246,0.04)"' if ours else ""
            rows_html += f"""
            <tr{row_style}>
              <td>{prefix}<span style="font-family:monospace;font-size:11px">{c['asin']}</span><br><span style="color:#64748b;font-size:10px">{c['brand']}</span></td>
              <td style="font-weight:600;color:white">${c['price']}</td>
              <td>{disc}</td>
              <td class="{rat_color}">{c['rating']}★</td>
              <td {rev_color}>{c['reviews']:,}</td>
              <td>{c['sales']:,}</td>
              <td style="color:#64748b">{c['budget']}</td>
              <td class="{ls_color}">{c['lscore']}</td>
              <td>#{c['bsr']}</td>
            </tr>"""

        st.markdown(f"""
        <div class="tbl-wrapper">
        <table class="dtbl">
          <thead><tr><th>ASIN / 品牌</th><th>价格</th><th>折扣</th><th>评分</th><th>评论量</th><th>月销估算</th><th>广告预算</th><th>Listing分</th><th>BSR</th></tr></thead>
          <tbody>{rows_html}</tbody>
        </table></div>""", unsafe_allow_html=True)

        c_adv, c_dis = st.columns(2)
        with c_adv:
            adv_rows = "".join(
                f'<div style="font-size:11px;color:#cbd5e1;display:flex;gap:5px;margin-bottom:4px"><span style="color:#34d399">+</span>{a}</div>'
                for a in ["24H 续航领先多数竞品","双配对功能差异化","USB-C 充电体验好","价格中档区间具备竞争力"]
            )
            st.markdown(f'<div class="adv-card"><div style="font-size:12px;font-weight:600;color:#34d399;margin-bottom:8px">✓ 我方优势</div>{adv_rows}</div>', unsafe_allow_html=True)
        with c_dis:
            dis_rows = "".join(
                f'<div style="font-size:11px;color:#cbd5e1;display:flex;gap:5px;margin-bottom:4px"><span style="color:#f87171">-</span>{a}</div>'
                for a in ["评论量仅1247，竞品均值9270（-87%）","Listing 质量分72，低于所有竞品","品牌知名度弱，无 Brand Story","BSR #247，落后 Tribit(#22)、Anker(#12)"]
            )
            st.markdown(f'<div class="dis-card"><div style="font-size:12px;font-weight:600;color:#f87171;margin-bottom:8px">✗ 我方劣势</div>{dis_rows}</div>', unsafe_allow_html=True)

        st.markdown('<div class="risk-box" style="margin-top:10px"><span style="font-weight:600">⚠ 最大风险：</span>评论量极度不足，在同类搜索页面中信任感最低，严重拖累转化率。</div>', unsafe_allow_html=True)
        st.markdown('<div class="prio-box" style="margin-top:6px"><span style="font-weight:600">→ 优先优化：</span>30天内Review糭还果2000是单一最高ROI动作，优先于任何广告优化。</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#94a3b8;margin-top:10px;margin-bottom:4px">建议动作</div>', unsafe_allow_html=True)
        st.markdown(action_list([
            "优先刷新 Review 数量：批量发送 Request a Review，目标30天内破2000",
            "Price 压至 $42.99 测试是否提升 CVR 并赶超 Tribit",
            "补充 Lifestyle 图和对比图，提升 Listing 质量分",
        ]), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MODULE 4 — KEYWORDS
# ─────────────────────────────────────────────────────────────

def render_keywords():
    sc = MOCK["scores"]["keywords"]
    kws = MOCK["keywords"]
    st.markdown('<div id="sec-keywords" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(mod_header("🔍", "关键词分析", "正常", sc, 20), unsafe_allow_html=True)
    with st.expander("展开详情", expanded=True):
        def fmt_rank(r, good=10, ok=20):
            if r<=good: return f'<span class="green-val">#{r}</span>'
            if r<=ok:   return f'<span class="amber-val">#{r}</span>'
            return f'<span class="red-val">#{r}</span>'
        def fmt_chg(c):
            if c>0: return f'<span class="green-val">↑{c}</span>'
            if c<0: return f'<span class="red-val">↓{abs(c)}</span>'
            return '<span style="color:#64748b">�n>'
        def fmt_opp(o):
            if o>=80: return f'<span class="green-val">{o}</span>'
            if o>=70: return f'<span class="blue-val">{o}</span>'
            return f'<span style="color:#64748b">{o}</span>'
        def fmt_vol(v):
            return f"{v//1000}K"

        rows = "".join(f"""
        <tr>
          <td style="font-weight:500;color:white">{k['kw']}</td>
          <td>{fmt_vol(k['vol'])}</td>
          <td style="color:{'#34d399' if k['trend']=='↑' else '#94a3b8'}">{k['trend']}</td>
          <td>{fmt_rank(k['org'])}</td>
          <td>{fmt_rank(k['spn'],5,10)}</td>
          <td>{fmt_chg(k['chg'])}</td>
          <td style="color:#94a3b8">{k['cov']}/5</td>
          <td>{fmt_opp(k['opp'])}</td>
          <td>{badge_html(k['status'])}</td>
        </tr>""" for k in kws)

        st.markdown(f"""
        <div class="tbl-wrapper">
        <table class="dtbl">
          <thead><tr><th>关键词</th><th>搜索量/月</th><th>趋势</th><th>自然排名</th><th>广告排名</th><th>7天变化</th><th>竞品覆盖</th><th>机会分</th><th>状态</th></tr></thead>
          <tbody>{rows}</tbody>
        </table></div>""", unsafe_allow_html=True)

        st.markdown(judgment("核心词自然排名偏低（前3词均在#12-32），'waterproof speaker'排名骤降，广告端部分词效率良好。"), unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#94a3b8;margin-top:10px;margin-bottom:4px">建议动作</div>', unsafe_allow_html=True)
        st.markdown(action_list([
            "'small bluetooth speaker' 自然排名#12，加码广告冲Top5",
            "'waterproof bluetooth speaker' 需Listing优化（标题/5点）后再推广告",
            "'bluetooth speaker'(45万搜量) 有机排名仅#18，是最大增量机会",
        ]), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MODULE 5 — ADS
# ─────────────────────────────────────────────────────────────

def render_ads():
    sc = MOCK["scores"]["ads"]
    s = MOCK["ads_summary"]
    camps = MOCK["campaigns"]
    ad_kws = MOCK["ad_kws"]
    st.markdown('<div id="sec-ads" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(mod_header("💰", "广告分析", "正常", sc, 20), unsafe_allow_html=True)
    with st.expander("展开详情", expanded=True):
        cols = st.columns(9)
        metrics = [
            ("总花费", f"${s['spend']:,}"),("曝光量",f"{s['impressions']//1000}K"),("点击量",f"{s['clicks']:,}"),
            ("CTR",f"{s['ctr']}%"),("CVR",f"{s['cvr']}%"),("CPC",f"${s['cpc']}"),
            ("转化数",str(s['conv'])),("ACOS",f"{s['acos']}%"),("ROAS",f"{s['roas']}x"),
        ]
        for col,(label,val) in zip(cols, metrics):
            with col:
                hl = label=="ACOS" and s['acos']>30
                clr = "#fbbf24" if hl else "white"
                hl_style = "border-color:rgba(245,158,11,0.5);background:rgba(245,158,11,0.05)" if hl else ""
                st.markdown(f"""
                <div class="diag-card" style="{hl_style};padding:10px">
                  <div class="diag-label">{label}</div>
                  <div style="font-size:15px;font-weight:700;color:{clr}">{val}</div>
                </div>""", unsafe_allow_html=True)

        tab_camp, tab_kw = st.tabs(["📋 广告活动", "🔑 关键词明细"])

        with tab_camp:
            rows = "".join(f"""
            <tr>
              <td style="color:white;font-weight:500">{c['name']}</td>
              <td style="color:white">${c['spend']}</td>
              <td>{c['impr']//1000}K</td><td>{c['clicks']}</td>
              <td>{c['ctr']}%</td><td>{c['cvr']}%</td>
              <td class="{'red-val' if c['acos']>35 else ('amber-val' if c['acos']>28 else 'green-val')}">{c['acos']}%</td>
              <td>{c['roas']}x</td>
              <td>{badge_html('good' if c['health']=='good' else 'warn')}</td>
            </tr>""" for c in camps)
            st.markdown(f"""
            <div class="tbl-wrapper">
            <table class="dtbl">
              <thead><tr><th>广告活动</th><th>花费</th><th>曝光</th><th>点击</th><th>CTR</th><th>CVR</th><th>ACOS</th><th>ROAS</th><th>状态</th></tr></thead>
              <tbody>{rows}</tbody>
            </table></div>""", unsafe_allow_html=True)

        with tab_kw:
            rows = "".join(f"""
            <tr style="{'background:rgba(239,68,68,0.04)' if k['status']=='abn' else ''}">
              <td style="color:white;font-weight:500">{k['kw']}</td>
              <td>${k['spend']}</td><td>{k['clicks']}</td>
              <td>{k['ctr']}%</td><td>${k['cpc']}</td>
              <td>{k['conv']}</td><td>{k['cvr']}%</td>
              <td class="{'red-val' if k['acos']>45 else ('amber-val' if k['acos']>30 else 'green-val')}">{k['acos']}%</td>
              <td>{badge_html(k['status'])}</td>
            </tr>""" for k in ad_kws)
            st.markdown(f"""
            <div class="tbl-wrapper">
            <table class="dtbl">
              <thead><tr><th>关键词</th><th>花费</th><th>点击</th><th>CTR</th><th>CPC</th><th>转化</th><th>CVR</th><th>ACOS</th><th>状态</th></tr></thead>
              <tbody>{rows}</tbody>
            </table></div>""", unsafe_allow_html=True)

        st.markdown(judgment("整体 ACOS 28.5% 尚可，但'waterproof speaker'和'ipx7 speaker'两词 ACOS 超50%，拖累整体效率。"), unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#94a3b8;margin-top:10px;margin-bottom:4px">建议动作</div>', unsafe_allow_html=True)
        st.markdown(action_list([
            "立即暂停/否词 'waterproof speaker'（ACOS 54.9%）和 'ipx7 speaker'（50.3%）",
            "提高 'small bluetooth speaker' 和 'outdoor speaker' 预算（ACOS 20-22%，机会词）",
            "开启 Sponsored Brands 视频广告，提升 CTR",
        ]), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MODULE 6 — 30-DAY ACTION PLAN
# ─────────────────────────────────────────────────────────────

def render_action_plan():
    st.markdown('<div id="sec-plan" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mod-header" style="border-left-color:#a78bfa">
      <div style="display:flex;align-items:center;gap:10px">
        <span style="font-size:16px">📋</span>
        <span class="mod-title">未来30天目标与运营方案</span>
      </div>
    </div>""", unsafe_allow_html=True)
    with st.expander("展开详情", expanded=True):
        col_a, col_b = st.columns(2)

        def plan_actions_html(actions):
            p_class = {"P0":"p0","P1":"p1","P2":"p2"}
            rows = ""
            for a in actions:
                rows += f"""
                <div style="display:flex;align-items:flex-start;gap:8px;background:rgba(30,41,59,0.6);border-radius:8px;padding:10px;margin-bottom:6px">
                  <span class="{p_class[a['p']]}">{a['p']}</span>
                  <div style="flex:1">
                    <div style="font-size:12px;color:white">{a['action']}</div>
                    <div style="font-size:11px;color:#64748b;margin-top:2px">{a['impact']}</div>
                  </div>
                  <span style="font-size:10px;color:#475569;flex-shrink:0">{a['d']}</span>
                </div>"""
            return rows

        with col_a:
            actions_a = [
                {"p":"P0","action":"暂停 'waterproof speaker' 和 'ipx7 speaker' 广告词","impact":"节省约$376/月无效花费","d":"D1"},
                {"p":"P1","action":"将售价从 $45.99 提升至 $47.99 A/B测试一周","impact":"利润率提升约4%，观察 CVR 变化","d":"D3"},
                {"p":"P1","action":"提高 'small bluetooth speaker' 预算20%（ACOS 20.1%）","impact":"预估新增约40次转化/月","d":"D5"},
                {"p":"P2","action":"优化 Listing Title 自然植入 'waterproof' 词","impact":"提升该词自然流量，减少广告依赖","d":"D7"},
                {"p":"P2","action":"申请 A+ Content（若未开通）","impact":"预估 CVR 提升5-8%","d":"D14"},
            ]
            st.markdown(f"""
            <div class="plan-card plan-a">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
                <span style="font-size:13px;font-weight:700;color:#60a5fa">方案 A · 利润最大化</span>
                <div style="text-align:right">
                  <div style="font-size:10px;color:#64748b">成功概率</div>
                  <div style="font-size:22px;font-weight:800;color:#60a5fa">62%</div>
                </div>
              </div>
              <div style="font-size:11px;color:#94a3b8;margin-bottom:12px">削减低效广告花费，小幅提价，聚焦高 ROAS 词，预计30天利润提升约37%。</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px">
                <div class="p-card"><div class="diag-label">目标利润/月</div><div style="font-size:15px;font-weight:700;color:white">$8,500</div><div style="font-size:11px;color:#34d399">+37% vs 当前</div></div>
                <div class="p-card"><div class="diag-label">当前利润/月</div><div style="font-size:15px;font-weight:700;color:#94a3b8">$6,200</div></div>
              </div>
              <div style="font-size:11px;font-weight:600;color:#94a3b8;margin-bottom:8px">关键动作清单</div>
              {plan_actions_html(actions_a)}
              <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);border-radius:8px;padding:10px;margin-top:8px">
                <div style="font-size:11px;font-weight:600;color:#fbbf24;margin-bottom:4px">风险提示</div>
                <div style="font-size:11px;color:#94a3b8">⚠ 提价初期可能带来 CVR 短暂下滑</div>
                <div style="font-size:11px;color:#94a3b8">⚠ 削减广告可能影响 BSR 排名动能</div>
              </div>
            </div>""", unsafe_allow_html=True)

        with col_b:
            actions_b = [
                {"p":"P0","action":"总广告预算提升至 $4,200/月（+48%）","impact":"预估新增约450次点击/月","d":"D1"},
                {"p":"P0","action":"30天内 Review 数量破 2000（Request a Review）","impact":"提升搜索权重和转化率","d":"D1"},
                {"p":"P1","action":"开启 Sponsored Brands 视频广告","impact":"提升上层流量认知","d":"D5"},
                {"p":"P1","action":"补充 2 张 Lifestyle 图 + 1 张对比图","impact":"预估 CTR 提升3-5%","d":"D7"},
                {"p":"P2","action":"将售价降至 $42.99 配合 Coupon 5%","impact":"提升 CVR，争抢 Tribit 价格段","d":"D10"},
            ]
            st.markdown(f"""
            <div class="plan-card plan-b">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
                <span style="font-size:13px;font-weight:700;color:#34d399">方案 B · 日均销量提升30%</span>
                <div style="text-align:right">
                  <div style="font-size:10px;color:#64748b">成功概率</div>
                  <div style="font-size:22px;font-weight:800;color:#34d399">55%</div>
                </div>
              </div>
              <div style="font-size:11px;color:#94a3b8;margin-bottom:12px">加大广告投入并优化关键词自然排名，同步提升 Listing 质量，目标月销量破 1274 单。</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px">
                <div class="p-card"><div class="diag-label">目标月销量</div><div style="font-size:15px;font-weight:700;color:white">1,274件</div><div style="font-size:11px;color:#34d399">+30% vs 当前</div></div>
                <div class="p-card"><div class="diag-label">当前月销量</div><div style="font-size:15px;font-weight:700;color:#94a3b8">980件</div></div>
              </div>
              <div style="font-size:11px;font-weight:600;color:#94a3b8;margin-bottom:8px">关键动作清单</div>
              {plan_actions_html(actions_b)}
              <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);border-radius:8px;padding:10px;margin-top:8px">
                <div style="font-size:11px;font-weight:600;color:#fbbf24;margin-bottom:4px">风险提示</div>
                <div style="font-size:11px;color:#94a3b8">⚠ 初期 ACOS 预计升至32-35%，需接受短期效率牺牲</div>
                <div style="font-size:11px;color:#94a3b8">⚠ Review 增长需4-6周才能体现在搜索权重上</div>
              </div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────

def render_footer():
    api_fns = ["getAsinOverview","getCategoryAnalysis","getBrandAnalysis","getCompetitorAnalysis","getKeywordAnalysis","getAdsAnalysis","getActionPlan"]
    fns_html = "".join(f'<span class="api-fn">{fn}()</span>' for fn in api_fns)
    st.markdown(f"""
    <div style="margin:0 24px 24px 24px;background:rgba(30,41,59,0.3);border:1px solid rgba(71,85,105,0.4);border-radius:12px;padding:16px">
      <div style="font-size:11px;font-weight:600;color:#94a3b8;margin-bottom:4px">数据接口说明</div>
      <div style="font-size:11px;color:#64748b">当前为 <span style="color:#fbbf24;font-weight:600">模拟数据</span>，所有数值仅供演示。可对接：Amazon Rainforest API &middot; Keepa API &middot; Amazon ABA &middot; Ads Console 报告 &middot; ERP 数据</div>
      <div class="api-fn-wrap">{fns_html}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    if "has_data" not in st.session_state:
        st.session_state.has_data = True
    if "current_asin" not in st.session_state:
        st.session_state.current_asin = "B0D54LVZK5"

    render_sidebar()
    render_topbar()

    # Input bar
    st.markdown('<div style="background:rgba(15,23,42,0.97);border-bottom:1px solid rgba(71,85,105,0.5);padding:8px 24px 6px 24px">', unsafe_allow_html=True)
    col_asin, col_site, col_period, col_btn, col_refresh, col_score = st.columns([4,1,2,1.5,1.5,2])

    with col_asin:
        asin_input = st.text_input("ASIN", value=st.session_state.current_asin, label_visibility="collapsed", placeholder="输入 ASIN...")
    with col_site:
        site = st.selectbox("站点", ["US","CA","UK","DE","JP"], label_visibility="collapsed")
    with col_period:
        period = st.radio("时间", ["日","周"], horizontal=True, label_visibility="collapsed")
    with col_btn:
        if st.button("🔍 开始分析", use_container_width=True):
            if asin_input.strip():
                with st.spinner(f"正在诊断 {asin_input.upper()}..."):
                    time.sleep(1.2)
                st.session_state.current_asin = asin_input.strip().upper()
                st.session_state.has_data = True
                st.rerun()
    with col_refresh:
        if st.button("↻ 刷新", use_container_width=True):
            st.rerun()
    with col_score:
        total = MOCK["scores"]["total"]
        overall = status_of(total)
        if st.session_state.has_data:
            c_map = {"优秀":"#34d399","较好":"#60a5fa","正常":"#fbbf24","异常":"#f87171"}
            st.markdown(f"""
            <div style="height:100%;display:flex;align-items:center;gap:8px;margin-top:4px">
              <span style="font-size:18px;font-weight:800;color:{c_map[overall]}">{total}/100</span>
              {badge_html(overall)}
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:11px;color:#475569;margin-top:4px;display:flex;gap:12px;align-items:center">
      <span>示例：</span>
      <span style="font-family:monospace">B0D54LVZK5</span>
      <span style="font-family:monospace">B08N5WRWNW</span>
      <span style="font-family:monospace">B07FZ8S74R</span>
      <span style="font-family:monospace">B09B8ZCPKQ</span>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not st.session_state.has_data:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:100px 0;color:#64748b">
          <div style="font-size:40px;margin-bottom:16px">🚀</div>
          <div style="font-size:14px">输入 ASIN 并点击「开始分析」</div>
        </div>""", unsafe_allow_html=True)
        return

    asin = st.session_state.current_asin
    p = MOCK["product"]
    st.markdown(f"""
    <div style="padding:14px 24px 8px 24px;display:flex;align-items:center;justify-content:space-between">
      <div>
        <span style="font-size:14px;font-weight:700;color:white">诊断报告 · </span>
        <span style="font-size:14px;font-weight:700;color:#60a5fa;font-family:monospace">{asin}</span>
        <span style="font-size:11px;color:#64748b;margin-left:10px">{p['category']} · 站点 {site} · 过去7天</span>
      </div>
    </div>""", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div style="padding:0 24px">', unsafe_allow_html=True)
        render_overview(asin)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding:0 24px;display:flex;flex-direction:column;gap:4px">', unsafe_allow_html=True)
    render_category()
    render_brand()
    render_competitors()
    render_keywords()
    render_ads()
    render_action_plan()
    st.markdown('</div>', unsafe_allow_html=True)

    render_footer()

main()
