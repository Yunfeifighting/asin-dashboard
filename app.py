import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(
    page_title="Yurise.ai Â· Amazonåå®¶è¿è¥å·¥å·",
    page_icon="ð",
    layout="wide",
    initial_sidebar_state="expanded",
)

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# GLOBAL CSS
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background:#0f172a !important; }
[data-testid="stHeader"]  { display:none !important; }
[data-testid="stToolbar"] { display:none !important; }
footer { display:none !important; }
.block-container { padding:0 !important; max-width:100% !important; }

/* ââ Sidebar ââ */
[data-testid="stSidebar"] {
  background:rgba(10,17,35,0.98) !important;
  border-right:1px solid rgba(71,85,105,0.35) !important;
  min-width:190px !important; max-width:190px !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { padding:0; }
[data-testid="stSidebarContent"] { padding:0 !important; }

/* ââ Module section header ââ */
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

/* ââ inputs ââ */
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

/* ââ expanders ââ */
[data-testid="stExpander"] {
  background:rgba(30,41,59,0.35) !important;
  border:1px solid rgba(71,85,105,0.5) !important; border-radius:0 0 12px 12px !important;
  border-top:none !important;
}
[data-testid="stExpander"] summary { color:#94a3b8 !important; font-weight:500 !important; font-size:12px !important; }
[data-testid="stExpander"] summary:hover { color:#93c5fd !important; }

/* ââ tabs ââ */
[data-testid="stTabs"] [role="tablist"] { background:#1e293b; border-radius:8px; padding:2px; border:1px solid #334155; }
[data-testid="stTabs"] [role="tab"] { color:#94a3b8 !important; border-radius:6px; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { background:#3b82f6 !important; color:white !important; }

/* ââ metrics ââ */
[data-testid="metric-container"] { background:rgba(30,41,59,0.5); border:1px solid rgba(71,85,105,0.6); border-radius:8px; padding:12px; }
[data-testid="stMetricLabel"] { color:#94a3b8 !important; font-size:11px !important; }
[data-testid="stMetricValue"] { color:#f1f5f9 !important; font-size:20px !important; }

/* ââ dataframe ââ */
[data-testid="stDataFrame"] { background:#1e293b !important; border-radius:8px; overflow:hidden; }

/* ââ plotly ââ */
.js-plotly-plot .plotly .bg { fill:#0f172a !important; }

/* ââ scrollbar ââ */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#1e293b; }
::-webkit-scrollbar-thumb { background:#475569; border-radius:3px; }

/* ââ cards ââ */
.diag-topbar { background:rgba(15,23,42,0.97); border-bottom:1px solid rgba(71,85,105,0.6); padding:10px 24px; }
.diag-card   { background:rgba(30,41,59,0.4); border:1px solid rgba(71,85,105,0.6); border-radius:12px; padding:16px; }
.diag-label  { font-size:11px; color:#94a3b8; margin-bottom:3px; }
.diag-val    { font-size:18px; font-weight:700; color:#f1f5f9; }
.diag-sub    { font-size:11px; color:#64748b; margin-top:2px; }
.diag-highlight { border-color:rgba(245,158,11,0.5) !important; background:rgba(245,158,11,0.06) !important; }

/* ââ badges ââ */
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

/* ââ judgment boxes ââ */
.judge-warn { background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.3); border-radius:8px; padding:10px 14px; font-size:12px; color:#fcd34d; margin:10px 0; }
.judge-info { background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.3); border-radius:8px; padding:10px 14px; font-size:12px; color:#93c5fd; margin:10px 0; }

/* ââ adv/dis cards ââ */
.adv-card { background:rgba(16,185,129,0.06); border:1px solid rgba(52,211,153,0.25); border-radius:8px; padding:12px; }
.dis-card { background:rgba(239,68,68,0.06); border:1px solid rgba(248,113,113,0.25); border-radius:8px; padding:12px; }
.risk-box { background:rgba(245,158,11,0.06); border:1px solid rgba(245,158,11,0.25); border-radius:8px; padding:10px 14px; font-size:12px; color:#fcd34d; }
.prio-box { background:rgba(59,130,246,0.06); border:1px solid rgba(59,130,246,0.25); border-radius:8px; padding:10px 14px; font-size:12px; color:#93c5fd; }

/* ââ action rows ââ */
.action-row { display:flex; align-items:flex-start; gap:8px; margin-bottom:6px; }
.action-icon { color:#60a5fa; margin-top:1px; flex-shrink:0; }

/* ââ tables ââ */
.tbl-wrapper { overflow-x:auto; border-radius:8px; border:1px solid rgba(71,85,105,0.5); }
table.dtbl { width:100%; border-collapse:collapse; font-size:12px; }
table.dtbl th { background:rgba(51,65,85,0.6); color:#94a3b8; padding:8px 12px; text-align:left; font-weight:500; border-bottom:1px solid rgba(71,85,105,0.5); white-space:nowraw; }
table.dtbl td { padding:8px 12px; color:#cbd5e1; border-bottom:1px solid rgba(71,85,105,0.35); }
table.dtbl tr:hover td { background:rgba(51,65,85,0.3); }
.red-val { color:#f87171; font-weight:700; }
.green-val { color:#34d399; font-weight:700; }
.amber-val { color:#fbbf24; font-weight:700; }
.blue-val { color:#60a5fa; }

/* ââ plan cards ââ */
.plan-card { border-radius:12px; padding:20px; }
.plan-a { background:rgba(59,130,246,0.06); border:1px solid rgba(96,165,250,0.3); }
.plan-b { background:rgba(16,185,129,0.06); border:1px solid rgba(52,211,153,0.3); }
.p0 { background:rgba(239,68,68,0.12); color:#f87171; border:1px solid rgba(248,113,113,0.3); padding:2px 7px; border-radius:4px; font-size:11px; font-weight:700; }
.p1 { background:rgba(245,158,11,0.12); color:#fbbf24; border:1px solid rgba(251,191,36,0.3); padding:2px 7px; border-radius:4px; font-size:11px; font-weight:700; }
.p2 { background:rgba(59,130,246,0.12); color:#60a5fa; border:1px solid rgba(96,165,250,0.3); padding:2px 7px; border-radius:4px; font-size:11px; font-weight:700; }

/* ââ p-card ââ */
.p-card { background:rgba(30,41,59,0.4); border-radius:8px; padding:10px; }

/* ââ sidebar nav ââ */
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

/* ââ section anchor ââ */
.sec-anchor { scroll-margin-top:10px; }

/* ââ api fn code display ââ */
.api-fn-wrap { display:flex; flex-wrap:wrap; gap:6px; margin-top:10px; padding-top:10px; border-top:1px solid rgba(71,85,105,0.4); }
.api-fn {
  font-family:monospace; font-size:10px; color:#60a5fa;
  background:rgba(59,130,246,0.1); border:1px solid rgba(96,165,250,0.25);
  padding:3px 9px; border-radius:5px;
}
</style>
""", unsafe_allow_html=True)

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# MOCK DATA
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
MOCK = {
    "product": {
        "asin": "B0D54LVZK5",
        "title": "SoundMax Pro X1 Portable Bluetooth Speaker, 360Â° Surround Sound, 24H Battery, IPX7 Waterproof, Dual Pairing, USB-C Charging",
        "brand": "SoundMax",
        "category": "Bluetooth Speakers",
        "price": 45.99, "rating": 4.2, "reviewCount": 1247,
        "inventoryStatus": "In Stock", "buyBoxStatus": "Won", "buyBoxWinRate": 94,
        "listingQualityScore": 72, "bsr": 247,
        "features": ["IPX7 Waterproof","24H Battery","360Â° Sound","Dual Pairing","USB-C"],
    },
    "scores": {"category":9,"brand":7,"competition":13,"keywords":14,"ads":14,"listing":10,"total":67},
    "scoreMeta": [
        {"key":"category",    "label":"åç±»è¡¨ç°",     "max":15},
        {"key":"brand",       "label":"åçè¡¨ç°",     "max":10},
        {"key":"competition", "label":"ç«åç«äºå",   "max":20},
        {"key":"keywords",    "label":"å³é®è¯è½å",   "max":20},
        {"key":"ads",         "label":"å¹¿åæç",     "max":20},
        {"key":"listing",     "label":"Listing&è¯è®º", "max":15},
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
        {"kw":"bluetooth speaker",          "vol":450000,"trend":"â","org":18,"spn":5, "chg":-3,"cov":5,"opp":82,"status":"opp"},
        {"kw":"portable bluetooth speaker", "vol":180000,"trend":"â","org":32,"spn":8, "chg":-2,"cov":5,"opp":74,"status":"opp"},
        {"kw":"small bluetooth speaker",    "vol":85000, "trend":"â","org":12,"spn":3, "chg": 2,"cov":4,"opp":88,"status":"good"},
        {"kw":"waterproof bluetooth speaker","vol":120000,"trend":"â","org":45,"spn":15,"chg":-5,"cov":5,"opp":65,"status":"risk"},
        {"kw":"outdoor bluetooth speaker",  "vol":65000, "trend":"â","org":22,"spn":6, "chg": 1,"cov":3,"opp":79,"status":"stable"},
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

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# HELPERS
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def status_of(score):
    if score >= 90: return "ä¼ç§"
    if score >= 75: return "è¾å¥½"
    if score >= 60: return "æ­£å¸¸"
    return "å¼å¸¸"

def badge_html(s):
    cls_map = {
        "ä¼ç§":"badge-excellent","è¾å¥½":"badge-good","æ­£å¸¸":"badge-normal","å¼å¸¸":"badge-bad",
        "opp":"badge-opp","good":"badge-excellent","stable":"badge-stable",
        "risk":"badge-risk","warn":"badge-warn","abn":"badge-abn",
    }
    label_map = {
        "ä¼ç§":"ä¼ç§","è¾å¥½":"è¾å¥½","æ­£å¸¸":"æ­£å¸¸","å¼å¸¸":"å¼å¸¸",
        "opp":"æºä¼","good":"è¯å¥½","stable":"ç¨³å®","risk":"é£é©","warn":"å¾ä¼å","abn":"å¼å¸¸",
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
        <span class="mod-score">{score}/{max_score}ç</span>
        <div style="width:60px;height:4px;background:#1e293b;border-radius:2px;overflow:hidden">
          <div style="height:100%;width:{sc_pct}%;background:{sc_clr};border-radius:2px"></div>
        </div>
        <span style="font-size:11px;font-weight:700;color:{sc_clr}">{sc_pct}%</span>
      </div>
    </div>"""

def action_list(actions):
    rows = "".join(
        f'<div class="action-row"><span class="action-icon">â</span>'
        f'<span style="font-size:12px;color:#cbd5e1">{a}</span></div>'
        for a in actions
    )
    return f'<div style="margin-top:8px">{rows}</div>'

def judgment(text, t="warn"):
    cls = "judge-warn" if t == "warn" else "judge-info"
    icon = "â " if t == "warn" else "â¹"
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

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# SIDEBAR  â  Elevator Navigation
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def render_sidebar():
    scores = MOCK["scores"]
    nav_items = [
        ("ð ", "æ¦è§æ»è§",   "sec-overview",   scores["total"],       100),
        ("ð", "åç±»åæ",   "sec-category",   scores["category"],    15),
        ("ð", "åçåæ",   "sec-brand",      scores["brand"],       10),
        ("ð¯", "ç«ååæ",   "sec-competitor", scores["competition"], 20),
        ("ð", "å³é®è¯åæ", "sec-keywords",   scores["keywords"],    20),
        ("ð°", "å¹¿ååæ",   "sec-ads",        scores["ads"],         20),
        ("ð", "30å¤©æ¹æ¡",   "sec-plan",       None,                  None),
    ]

    total = scores["total"]
    overall = status_of(total)
    c_map = {"ä¼ç§":"#34d399","è¾å¥½":"#60a5fa","æ­£å¸¸":"#fbbf24","å¼å¸¸":"#f87171"}
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
            <div style="width:26px;height:26px;background:linear-gradient(135deg,#3b82f6,#7c3aed);border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:14px">ð</div>
            <div>
              <div class="nav-logo-name">Yurise.ai</div>
              <div class="nav-logo-sub">Amazonåå®¶è¿è¥å·¥å·</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:8px;background:rgba(30,41,59,0.5);border:1px solid rgba(71,85,105,0.4);border-radius:8px;padding:8px 10px;margin-top:8px">
            <div style="text-align:center">
              <div style="font-size:22px;font-weight:800;color:{ring_clr};line-height:1">{total}</div>
              <div style="font-size:9px;color:#475569">/100</div>
            </div>
            <div style="flex:1">
              <div style="font-size:11px;color:#94a3b8;margin-bottom:4px">ç»¼åå¥åº·å</div>
              <div style="height:4px;background:#1e293b;border-radius:2px;overflow:hidden">
                <div style="height:100%;width:{total}%;background:{ring_clr};border-radius:2px"></div>
            </div>
                <div style="font-size:10px;color:{ring_clr};font-weight:600;margin-top:3px">{overall}</div>
            </div>
          </div>
        </div>
        <div class="nav-section-label">æ¨¡åå¯¼èª</div>
        {items_html}
        <div class="nav-divider"></div>
        <div style="padding:8px 18px;font-size:10px;color:#334155;line-height:1.6">
          æ¨¡ææ°æ®æ¨¡å¼<br>å¯æ¿æ¢ä¸ºçå® API
        </div>
        """, unsafe_allow_html=True)

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# TOP BAR
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def render_topbar():
    st.markdown("""
    <div class="diag-topbar" style="display:flex;align-items:center;justify-content:space-between">
      <div style="display:flex;align-items:center;gap:10px">
        <div style="width:22px;height:22px;background:linear-gradient(135deg,#3b82f6,#7c3aed);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:13px">ð</div>
        <span style="font-size:15px;font-weight:800;background:linear-gradient(90deg,#60a5fa,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-0.3px">Yurise.ai</span>
        <span style="font-size:12px;color:#64748b">Amazonåå®¶è¿è¥å·¥å·</span>
      </div>
      <span style="font-size:11px;color:#64748b">
        <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#f59e0b;margin-right:5px"></span>
        æ¨¡ææ°æ®æ¨¡å¼ Â· å¯æ¿æ¢ä¸ºçå® API æ°æ®
      </span>
    </div>
    """, unsafe_allow_html=True)

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# OVERVIEW
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def render_overview(asin):
    p = MOCK["product"]
    scores = MOCK["scores"]
    meta = MOCK["scoreMeta"]
    total = scores["total"]
    overall = status_of(total)
    color_map = {"ä¼ç§":"#34d399","è¾å¥½":"#60a5fa","æ­£å¸¸":"#fbbf24","å¼å¸¸":"#f87171"}
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
                ("åç",p["brand"],"#60a5fa"),
                ("ä»·æ ¼",f"${p['price']}","white"),
                ("è¯å/è¯è®º",f"{p['rating']}â / {p['reviewCount']:,}","#fbbf24"),
                ("BSR",f"#{p['bsr']}","#f87171"),
                ("åºå­",p["inventoryStatus"],"#34d399"),
                ("Buy Box",f"{p['buyBoxStatus']} ({p['buyBoxWinRate']}%)","white"),
                ("Listingå",f"{p['listingQualityScore']}/100","#fbbf24"),
                ("æ ¸å¿åè½"," Â· ".join(p["features"][:2]),"#94a3b8"),
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
            <span style="font-size:13px;font-weight:600;color:white">å¥åº·è¯å</span>
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
            <span style="color:#e2e8f0">ç»¼åè¯æ­ï¼</span>è¯¥ ASIN å¤äº
            <span style="color:#fbbf24;font-weight:600">æ­£å¸¸</span>æ°´å¹³ï¼è¯è®ºéä¸è¶³æ¯æ ¸å¿ç¶é¢ï¼å³é®è¯èªç¶æµéæè¾å¤§æåç©ºé´ï¼å¹¿åå­å¨æµªè´¹ã
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    issues = [
        "è¯è®ºéä»1,247ï¼ç«ååå¼è¶9,000ï¼è½¬åä¿¡ä»»åº¦ä¸¥éä¸è¶³",
        "Listing è´¨éå72åï¼æ»¡å100ï¼ï¼å¾çåæè¿°æä¼åç©ºé´",
        "BSR è¿ç»­7å¤©ä¸æ»ï¼å½å #247ï¼éå¹¿åå¹²é¢",
    ]
    opportunities = [
        "'bluetooth speaker'(45ä¸æé)èªç¶æå#18ï¼è¿å¥Top10å¯å¤§å¹æåææºæµé",
        "'small bluetooth speaker'èªç¶æå#12ï¼å¹¿åACOSä»20.1%ï¼å¯æ¾é",
        "ç±»ç®éæ±æ´ä½å¥åº·å¢é¿ï¼ç«åæ ææ¾ä»·æ ¼æ¤åæ²³",
    ]
    suggestions = [
        "30å¤©å Review æ°éå²ç ´2,000ï¼Request a Review + Vineï¼",
        "æå ACOS>50% çå¹¿åè¯ï¼èççº¦$376/æ",
        "å¼å¯ Sponsored Brands è§é¢å¹¿åï¼æååçè®¤ç¥",
    ]
    for col, title, icon, color, items in [
        (c1, "æ ¸å¿é®é¢ Top 3", "â ", "#f87171", issues),
        (c2, "æ ¸å¿æºä¼ Top 3", "â", "#60a5fa", opportunities),
        (c3, "å»ºè®®å¨ä½ Top 3", "â¡", "#34d399", suggestions),
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

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# MODULE 1 â CATEGORY
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def render_category():
    d = MOCK
    sc = MOCK["scores"]["category"]
    st.markdown('<div id="sec-category" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(mod_header("ð", "åç±»åæ", "æ­£å¸¸", sc, 15), unsafe_allow_html=True)
    with st.expander("å±å¼è¯¦æ", expanded=True):
        c1,c2,c3,c4,c5 = st.columns(5)
        cols_data = [
            (c1, "å½æ¥éé", "33", "ä»¶", "è¿7æ¥åå¼38.6ä»¶", True),
            (c2, "ç±»ç®åå¼", "37.1", "ä»¶", "Top100æ¥å", False),
            (c3, "ç±»ç®ä»½é¢", "1.5%", "", "è¿ç»­3æ¥ä¸æ»", True),
            (c4, "BSRæå",  "#247", "", "7å¤©è·36ä½", True),
            (c5, "Top10åå¼","191", "ä»¶", "å·®è·Ã5.8å", False),
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
        fig.add_trace(go.Scatter(x=d["trend_dates"], y=d["our_sales"], name="ææ¹éé",
            line=dict(color="#60a5fa", width=2), fill="tozeroy",
            fillcolor="rgba(96,165,250,0.1)"))
        fig.add_trace(go.Scatter(x=d["trend_dates"], y=d["cat_avg"], name="ç±»ç®åå¼",
            line=dict(color="#a78bfa", width=1.5, dash="dash")))
        fig.update_layout(dark_layout(title="7æ¥ééè¶å¿å¯¹æ¯", height=200))
        st.plotly_chart(fig, use_container_width=True, config=plotly_cfg())

        brands = d["top_brands"]
        fig2 = go.Figure(go.Bar(
            x=[b["share"] for b in brands], y=[b["brand"] for b in brands],
            orientation="h",
            marker=dict(color=["#34d399" if b["brand"]=="SoundMax" else "#3b82f6" for b in brands]),
        ))
        fig2.update_layout(dark_layout(title="ç±»ç®åçä»½é¢åå¸ (%)", height=200, xaxis_title="å¸åºä»½é¢ (%)"))
        st.plotly_chart(fig2, use_container_width=True, config=plotly_cfg())

        st.markdown(judgment("ééè¶å¿7æ¥è¿ç»­ä¸æ»ï¼å½åä»½é¢1.5%ä½äºç±»ç®åå¼ï¼ç±»ç®æ´ä½ä¿æå¢é¿ï¼åç±»éæ±å¥åº·ã"), unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#94a3b8;margin-top:10px;margin-bottom:4px">å»ºè®®å¨ä½</div>', unsafe_allow_html=True)
        st.markdown(action_list([
            "ç«å³æ£æ¥æ¯å¦æå·®è¯æ Q&A å½±åè½¬å",
            "å å¼ºå³é®è¯å¹¿åææ¾ï¼é»æ­¢ BSR ç»§ç»­ä¸æ»",
            "èè Coupon æ Prime Exclusive Discount åºæ¿è½¬å",
        ]), unsafe_allow_html=True)

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# MODULE 2 â BRAND
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def render_brand():
    d = MOCK
    sc = MOCK["scores"]["brand"]
    st.markdown('<div id="sec-brand" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(mod_header("ð", "åçåæ", "æ­£å¸¸", sc, 10), unsafe_allow_html=True)
    with st.expander("å±å¼è¯¦æ", expanded=True):
        c1,c2,c3,c4 = st.columns(4)
        for col, label, val, sub, hl in [
            (c1,"åçç±»ç®æå","#8","Top10åç",False),
            (c2,"åçå¸åºä»½é¢","4.2%","è¿å»7å¤©",False),
            (c3,"æ¬ASINè´¡ç®åº¦","42%","å åçæ»éé",True),
            (c4,"åçå¢é¿WoW","-3.2%","ç±»ç®åæ+1.4%",True),
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
            x=[r["date"] for r in bt], y=[r["brandIdx"] for r in bt], name="åçææ°",
            line=dict(color="#60a5fa", width=2), mode="lines+markers",
            marker=dict(size=4, color="#60a5fa")))
        fig.add_trace(go.Scatter(
            x=[r["date"] for r in bt], y=[r["catIdx"] for r in bt], name="ç±»ç®ææ°",
            line=dict(color="#a78bfa", width=1.5, dash="dash"), mode="lines"))
        fig.add_hline(y=100, line=dict(color="#334155", dash="dot"), annotation_text="åºåçº¿")
        fig.update_layout(dark_layout(title="åç vs ç±»ç®è¶å¿ææ°ï¼åºå=100ï¼", height=200, yaxis_range=[78,115]))
        st.plotly_chart(fig, use_container_width=True, config=plotly_cfg())

        st.markdown(judgment("åçæ´ä½å¨ä¸æ»ï¼-3.2% WoWï¼ï¼èç±»ç®åæå¢é¿1.4%ï¼æ¬ ASIN è´¡ç®åç42%ééï¼åçå¿è½åå¼±ã"), unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#94a3b8;margin-top:10px;margin-bottom:4px">å»ºè®®å¨ä½</div>', unsafe_allow_html=True)
        st.markdown(action_list([
            "æ£æ¥åçä¸å¶ä» ASIN æ¯å¦å­å¨ Review é®é¢æç´¯åçæ´ä½",
            "èèå¼å¯ Sponsored Brands å¹¿åï¼å¼ºååçè®¤ç¥åº¦",
            "è¯ä¼°æ¯å¦éè¦æ¨åºæ°æ¬¾ ASIN è¡¥åäº§åçº¿",
        ]), unsafe_allow_html=True)

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# MODULE 3 â COMPETITORS
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def render_competitors():
    sc = MOCK["scores"]["competition"]
    comps = MOCK["competitors"]
    st.markdown('<div id="sec-competitor" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(mod_header("ð¯", "ç«ååæ", "æ­£å¸¸", sc, 20), unsafe_allow_html=True)
    with st.expander("å±å¼è¯¦æ", expanded=True):
        rows_html = ""
        for c in comps:
            ours = c["ours"]
            prefix = '<span style="background:rgba(59,130,246,0.2);color:#60a5fa;border:1px solid rgba(96,165,250,0.4);padding:1px 6px;border-radius:3px;font-size:10px;margin-right:4px">ææ¹</span>' if ours else ""
            rev_color = 'class="red-val"' if ours and c["reviews"]<3000 else ""
            rat_color = "green-val" if c["rating"]>=4.5 else ("amber-val" if c["rating"]>=4.0 else "red-val")
            ls_color  = "green-val" if c["lscore"]>=85 else ("amber-val" if c["lscore"]>=75 else "red-val")
            disc = f'<span class="green-val"al">-{c["discount"]}%</span>' if c["discount"]>0 else "â"
            row_style = ' style="background:rgba(59,130,246,0.04)"' if ours else ""
            rows_html += f"""
            <tr{row_style}>
              <td>{prefix}<span style="font-family:monospace;font-size:11px">{c['asin']}</span><br><span style="color:#64748b;font-size:10px">{c['brand']}</span></td>
              <td style="font-weight:600;color:white">${c['price']}</td>
              <td>{disc}</td>
              <td class="{rat_color}">{c['rating']}â</td>
              <td {rev_color}>{c['reviews']:,}</td>
              <td>{c['sales']:,}</td>
              <td style="color:#64748b">{c['budget']}</td>
              <td class="{ls_color}">{c['lscore']}</td>
              <td>#{c['bsr']}</td>
            </tr>"""

        st.markdown(f"""
        <div class="tbl-wrapper">
        <table class="dtbl">
          <thead><tr><th>ASIN / åç</th><th>ä»·æ ¼</th><th>ææ£</th><th>è¯å</th><th>è¯è®ºé</th><th>æéä¼°ç®</th><th>å¹¿åé¢ç®</th><th>Listingå</th><th>BSR</th></tr></thead>
          <tbody>{rows_html}</tbody>
        </table></div>""", unsafe_allow_html=True)

        c_adv, c_dis = st.columns(2)
        with c_adv:
            adv_rows = "".join(
                f'<div style="font-size:11px;color:#cbd5e1;display:flex;gap:5px;margin-bottom:4px"><span style="color:#34d399">+</span>{a}</div>'
                for a in ["24H ç»­èªé¢åå¤æ°ç«å","åéå¯¹åè½å·®å¼å","USB-C åçµä½éªå¥½","ä»·æ ¼ä¸­æ¡£åºé´å·å¤ç«äºå"]
            )
            st.markdown(f'<div class="adv-card"><div style="font-size:12px;font-weight:600;color:#34d399;margin-bottom:8px">â ææ¹ä¼å¿</div>{adv_rows}</div>', unsafe_allow_html=True)
        with c_dis:
            dis_rows = "".join(
                f'<div style="font-size:11px;color:#cbd5e1;display:flex;gap:5px;margin-bottom:4px"><span style="color:#f87171">-</span>{a}</div>'
                for a in ["è¯è®ºéä»1247ï¼ç«ååå¼9270ï¼-87%ï¼","Listing è´¨éå72ï¼ä½äºææç«å","åçç¥ååº¦å¼±ï¼æ  Brand Story","BSR #247ï¼è½å Tribit(#22)ãAnker(#12)"]
            )
            st.markdown(f'<div class="dis-card"><div style="font-size:12px;font-weight:600;color:#f87171;margin-bottom:8px">â ææ¹å£å¿</div>{dis_rows}</div>', unsafe_allow_html=True)

        st.markdown('<div class="risk-box" style="margin-top:10px"><span style="font-weight:600">â  æå¤§é£é©ï¼</span>è¯è®ºéæåº¦ä¸è¶³ï¼å¨åç±»æç´¢é¡µé¢ä¸­ä¿¡ä»»ææä½ï¼ä¸¥éæç´¯è½¬åçã</div>', unsafe_allow_html=True)
        st.markdown('<div class="prio-box" style="margin-top:6px"><span style="font-weight:600">â ä¼åä¼åï¼</span>30å¤©åReviewç ´2000æ¯åä¸æé«ROIå¨ä½ï¼ä¼åäºä»»ä½å¹¿åä¼åã</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#94a3b8;margin-top:10px;margin-bottom:4px">å»ºè®®å¨ä½</div>', unsafe_allow_html=True)
        st.markdown(action_list([
            "ä¼åå·æ° Review æ°éï¼æ¹éåé Request a Reviewï¼ç®æ 30å¤©åç ´2000",
            "Price åè³ $42.99 æµè¯æ¯å¦æå CVR å¹¶èµ¶è¶ Tribit",
            "è¡¥å Lifestyle å¾åå¯¹æ¯å¾ï¼æå Listing è´¨éå",
        ]), unsafe_allow_html=True)

# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# MODULE 4 â KEYWORDS
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def render_keywords():
    sc = MOCK["scores"]["keywords"]
    kws = MOCK["keywords"]
    st.markdown('<div id="sec-keywords" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(mod_header("ð", "å³é®è¯åæ", "æ­£å¸¸", sc, 20), unsafe_allow_html=True)
    with st.expander("å±å¼è¯¦æ", expanded=True):
        def fmt_rank(r, good=10, ok=20):
            if r<=good: return f'<span class="green-val">#{r}</span>'
            if r<=ok:   return f'<span class="amber-val">#{r}</span>'
            return f'<span class="red-val">#{r}</span>'
        def fmt_chg(c):
            if c>0: return f'<span class="green-val">â{c}</span>'
            if c<0: return f'<span class="red-val">â{abs(c)}</span>'
            return '<span style="color:#64748b">â</span>'
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
          <td style="color:{'#34d399' if k['trend']=='â' else '#94a3b8'}">{k['trend']}</td>
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
          <thead><tr><th>å³é®è¯</th><th>æç´¢é/æ</th><th>è¶å¿</th><th>èªç¶æå</th><th>å¹¿åæå</th><th>7å¤©åå</th><th>ç«åè¦ç</th><th>æºä¼å</th><th>ç¶æ</th></tr></thead>
          <tbody>{rows}</tbody>
        </table></div>""", unsafe_allow_html=True)

        st.markdown(judgment("æ ¸å¿è¯èªç¶æååä½ï¼å3è¯åå¨#12-32ï¼ï¼'waterproof speaker'æåéª¤éï¼å¹¿åç«¯é¨åè¯æçè¯å¥½ã"), unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#94a3b8;margin-top:10px;margin-bottom:4px">å»ºè®®å¨ä½</div>', unsafe_allow_html=True)
        st.markdown(action_list([
            "'small bluetooth speaker' èªç¶æå#12ï¼å ç å¹¿åå²Top5",
            "'waterproof bluetooth speaker' éListingä¼åï¼æ é¢/5ç¹ï¼ååæ¨å¹¿å",
            "'bluetooth speaker'(45ä¸æé) ææºæåä»#18ï¼æ¯æå¤§å¢éæºä¼",
        ]), unsafe_allow_html=True)

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# MODULE 5 â ADS
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def render_ads():
    sc = MOCK["scores"]["ads"]
    s = MOCK["ads_summary"]
    camps = MOCK["campaigns"]
    ad_kws = MOCK["ad_kws"]
    st.markdown('<div id="sec-ads" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(mod_header("ð°", "å¹¿ååæ", "æ­£å¸¸", sc, 20), unsafe_allow_html=True)
    with st.expander("å±å¼è¯¦æ", expanded=True):
        cols = st.columns(9)
        metrics = [
            ("æ»è±è´¹", f"${s['spend']:,}"),("æåé",f"{s['impressions']//1000}K"),("ç¹å»é",f"{s['clicks']:,}"),
            ("CTR",f"{s['ctr']}%"),("CVR",f"{s['cvr']}%"),("CPC",f"${s['cpc']}"),
            ("è½¬åæ°",str(s['conv'])),("ACOS",f"{s['acos']}%"),("ROAS",f"{s['roas']}x"),
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

        tab_camp, tab_kw = st.tabs(["ð å¹¿åæ´»å¨", "ð å³é®è¯æç»"])

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
              <thead><tr><th>å¹¿åæ´»å¨</th><th>è±è´¹</th><th>æå</th><th>ç¹å»</th><th>CTR</th><th>CVR</th><th>ACOS</th><th>ROAS</th><th>ç¶æ</th></tr></thead>
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
              <thead><tr><th>å³é®è¯</th><th>è±è´¹</th><th>ç¹å»</th><th>CTR</th><th>CPC</th><th>è½¬å</th><th>CVR</th><th>ACOS</th><th>ç¶æ</th></tr></thead>
              <tbody>{rows}</tbody>
            </table></div>""", unsafe_allow_html=True)

        st.markdown(judgment("æ´ä½ ACOS 28.5% å°å¯ï¼ä½'waterproof speaker'å'ipx7 speaker'ä¸¤è¯ ACOS è¶50%ï¼æç´¯æ´ä½æçã"), unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#94a3b8;margin-top:10px;margin-bottom:4px">å»ºè®®å¨ä½</div>', unsafe_allow_html=True)
        st.markdown(action_list([
            "ç«å³æå/å¦è¯ 'waterproof speaker'ï¼ACOS 54.9%ï¼å 'ipx7 speaker'ï¼50.3%ï¼",
            "æé« 'small bluetooth speaker' å 'outdoor speaker' é¢ç®ï¼ACOS 20-22%ï¼æºä¼è¯ï¼",
            "å¼å¯ Sponsored Brands è§é¢å¹¿åï¼æå CTR",
        ]), unsafe_allow_html=True)

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# MODULE 6 â 30-DAY ACTION PLAN
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def render_action_plan():
    st.markdown('<div id="sec-plan" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mod-header" style="border-left-color:#a78bfa">
      <div style="display:flex;align-items:center;gap:10px">
        <span style="font-size:16px">ð</span>
        <span class="mod-title">æªæ¥30å¤©ç®æ ä¸è¿è¥æ¹æ¡</span>
      </div>
    </div>""", unsafe_allow_html=True)
    with st.expander("å±å¼è¯¦æ", expanded=True):
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
                {"p":"P0","action":"æå 'waterproof speaker' å 'ipx7 speaker' å¹¿åè¯","impact":"èççº¦$376/ææ æè±è´¹","d":"D1"},
                {"p":"P1","action":"å°å®ä»·ä» $45.99 æåè³ $47.99 A/Bæµè¯ä¸å¨","impact":"å©æ¶¦çæåçº¦4%ï¼è§å¯ CVR åå","d":"D3"},
                {"p":"P1","action":"æé« 'small bluetooth speaker' é¢ç®20%ï¼ACOS 20.1%ï¼","impact":"é¢ä¼°æ°å¢çº¦40æ¬¡è½¬å/æ","d":"D5"},
                {"p":"P2","action":"ä¼å Listing Title èªç¶æ¤å¥ 'waterproof' è¯","impact":"æåè¯¥è¯èªç¶æµéï¼åå°å¹¿åä¾èµ","d":"D7"},
                {"p":"P2","action":"ç³è¯· A+ Contentï¼è¥æªå¼éï¼","impact":"é¢ä¼° CVR æå5-8%","d":"D14"},
            ]
            st.markdown(f"""
            <div class="plan-card plan-a">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
                <span style="font-size:13px;font-weight:700;color:#60a5fa">æ¹æ¡ A Â· å©æ¶¦æå¤§å</span>
                <div style="text-align:right">
                  <div style="font-size:10px;color:#64748b">æåæ¦ç</div>
                  <div style="font-size:22px;font-weight:800;color:#60a5fa">62%</div>
                </div>
              </div>
              <div style="font-size:11px;color:#94a3b8;margin-bottom:12px">ååä½æå¹¿åè±è´¹ï¼å°å¹æä»·ï¼èç¦é« ROAS è¯ï¼é¢è®¡30å¤©å©æ¶¦æåçº¦37%ã</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px">
                <div class="p-card"><div class="diag-label">ç®æ å©æ¶¦/æ</div><div style="font-size:15px;font-weight:700;color:white">$8,500</div><div style="font-size:11px;color:#34d399">+37% vs å½å</div></div>
                <div class="p-card"><div class="diag-label">å½åå©æ¶¦/æ</div><div style="font-size:15px;font-weight:700;color:#94a3b8">$6,200</div></div>
              </div>
              <div style="font-size:11px;font-weight:600;color:#94a3b8;margin-bottom:8px">å³é®å¨ä½æ¸å</div>
              {plan_actions_html(actions_a)}
              <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);border-radius:8px;padding:10px;margin-top:8px">
                <div style="font-size:11px;font-weight:600;color:#fbbf24;margin-bottom:4px">é£é©æç¤º</div>
                <div style="font-size:11px;color:#94a3b8">â  æä»·åæå¯è½å¸¦æ¥ CVR ç­æä¸æ»</div>
                <div style="font-size:11px;color:#94a3b8">â  ååå¹¿åå¯è½å½±å BSR æåå¨è½</div>
              </div>
            </div>""", unsafe_allow_html=True)

        with col_b:
            actions_b = [
                {"p":"P0","action":"æ»å¹¿åé¢ç®æåè³ $4,200/æï¼+48%ï¼","impact":"é¢ä¼°æ°å¢çº¦450æ¬¡ç¹å»/æ","d":"D1"},
                {"p":"P0","action":"30å¤©å Review æ°éç ´ 2000ï¼Request a Reviewï¼","impact":"æåæç´¢æéåè½¬åç","d":"D1"},
                {"p":"P1","action":"å¼å¯ Sponsored Brands è§é¢å¹¿å","impact":"æåä¸å±æµéè®¤ç¥","d":"D5"},
                {"p":"P1","action":"è¡¥å 2 å¼  Lifestyle å¾ + 1 å¼ å¯¹æ¯å¾","impact":"é¢ä¼° CTR æå3-5%","d":"D7"},
                {"p":"P2","action":"å°å®ä»·éè³ $42.99 éå Coupon 5%","impact":"æå CVRï¼äºæ¢ Tribit ä»·æ ¼æ®µ","d":"D10"},
            ]
            st.markdown(f"""
            <div class="plan-card plan-b">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
                <span style="font-size:13px;font-weight:700;color:#34d399">æ¹æ¡ B Â· æ¥åééæå30%</span>
                <div style="text-align:right">
                  <div style="font-size:10px;color:#64748b">æåæ¦ç</div>
                  <div style="font-size:22px;font-weight:800;color:#34d399">55%</div>
                </div>
              </div>
              <div style="font-size:11px;color:#94a3b8;margin-bottom:12px">å å¤§å¹¿åæå¥å¹¶ä¼åå³é®è¯èªç¶æåï¼åæ­¥æå Listing è´¨éï¼ç®æ æééç ´ 1274 åã</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px">
                <div class="p-card"><div class="diag-label">ç®æ æéé</div><div style="font-size:15px;font-weight:700;color:white">1,274ä»¶</div><div style="font-size:11px;color:#34d399">+30% vs å½å</div></div>
                <div class="p-card"><div class="diag-label">å½åæéé</div><div style="font-size:15px;font-weight:700;color:#94a3b8">980ä»¶</div></div>
              </div>
              <div style="font-size:11px;font-weight:600;color:#94a3b8;margin-bottom:8px">å³é®å¨ä½æ¸å</div>
              {plan_actions_html(actions_b)}
              <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);border-radius:8px;padding:10px;margin-top:8px">
                <div style="font-size:11px;font-weight:600;color:#fbbf24;margin-bottom:4px">é£é©æç¤º</div>
                <div style="font-size:11px;color:#94a3b8">â  åæ ACOS é¢è®¡åè³32-35%ï¼éæ¥åç­ææççºç²</div>
                <div style="font-size:11px;color:#94a3b8">â  Review å¢é¿é4-6å¨æè½ä½ç°å¨æç´¢æéä¸</div>
              </div>
            </div>""", unsafe_allow_html=True)

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# FOOTER
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def render_footer():
    api_fns = ["getAsinOverview","getCategoryAnalysis","getBrandAnalysis","getCompetitorAnalysis","getKeywordAnalysis","getAdsAnalysis","getActionPlan"]
    fns_html = "".join(f'<span class="api-fn">{fn}()</span>' for fn in api_fns)
    st.markdown(f"""
    <div style="margin:0 24px 24px 24px;background:rgba(30,41,59,0.3);border:1px solid rgba(71,85,105,0.4);border-radius:12px;padding:16px">
      <div style="font-size:11px;font-weight:600;color:#94a3b8;margin-bottom:4px">æ°æ®æ¥å£è¯´æ</div>
      <div style="font-size:11px;color:#64748b">å½åä¸º <span style="color:#fbbf24;font-weight:600">æ¨¡ææ°æ®</span>ï¼æææ°å¼ä»ä¾æ¼ç¤ºãå¯å¯¹æ¥ï¼Amazon Rainforest API &middot; Keepa API &middot; Amazon ABA &middot; Ads Console æ¥å &middot; ERP æ°æ®</div>
      <div class="api-fn-wrap">{fns_html}</div>
    </div>
    """, unsafe_allow_html=True)

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# MAIN
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

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
        asin_input = st.text_input("ASIN", value=st.session_state.current_asin, label_visibility="collapsed", placeholder="è¾å¥ ASIN...")
    with col_site:
        site = st.selectbox("ç«ç¹", ["US","CA","UK","DE","JP"], label_visibility="collapsed")
    with col_period:
        period = st.radio("æ¶é´", ["æ¥","å¨"], horizontal=True, label_visibility="collapsed")
    with col_btn:
        if st.button("ð å¼å§åæ", use_container_width=True):
            if asin_input.strip():
                with st.spinner(f"æ­£å¨è¯æ­ {asin_input.upper()}..."):
                    time.sleep(1.2)
                st.session_state.current_asin = asin_input.strip().upper()
                st.session_state.has_data = True
                st.rerun()
    with col_refresh:
        if st.button("â» å·æ°", use_container_width=True):
            st.rerun()
    with col_score:
        total = MOCK["scores"]["total"]
        overall = status_of(total)
        if st.session_state.has_data:
            c_map = {"ä¼ç§":"#34d399","è¾å¥½":"#60a5fa","æ­£å¸¸":"#fbbf24","å¼å¸¸":"#f87171"}
            st.markdown(f"""
            <div style="height:100%;display:flex;align-items:center;gap:8px;margin-top:4px">
              <span style="font-size:18px;font-weight:800;color:{c_map[overall]}">{total}/100</span>
              {badge_html(overall)}
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:11px;color:#475569;margin-top:4px;display:flex;gap:12px;align-items:center">
      <span>ç¤ºä¾ï¼</span>
      <span style="font-family:monospace">B0D54LVZK5</span>
      <span style="font-family:monospace">B08N5WRWNW</span>
      <span style="font-family:monospace">B07FZ8S74R</span>
      <span style="font-family:monospace">B09B8ZCPKQ</span>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not st.session_state.has_data:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:100px 0;color:#64748b">
          <div style="font-size:40px;margin-bottom:16px">ð</div>
          <div style="font-size:14px">è¾å¥ ASIN å¹¶ç¹å»ãå¼å§åæã</div>
        </div>""", unsafe_allow_html=True)
        return

    asin = st.session_state.current_asin
    p = MOCK["product"]
    st.markdown(f"""
    <div style="padding:14px 24px 8px 24px;display:flex;align-items:center;justify-content:space-between">
      <div>
        <span style="font-size:14px;font-weight:700;color:white">è¯æ­æ¥å Â· </span>
        <span style="font-size:14px;font-weight:700;color:#60a5fa;font-family:monospace">{asin}</span>
        <span style="font-size:11px;color:#64748b;margin-left:10px">{p['category']} Â· ç«ç¹ {site} Â· è¿å»7å¤©</span>
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
