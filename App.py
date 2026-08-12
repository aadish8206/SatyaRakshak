import streamlit as st

# ==============================================================================
# PAGE CONFIG
# ==============================================================================
st.set_page_config(
    page_title="SatyaRakshak Times",
    page_icon="🗞️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# GLOBAL CSS — NEWSPAPER THEME
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800;900&family=Merriweather:wght@300;400;700&family=Old+Standard+TT:wght@400;700&display=swap');

:root{
--paper:#F8F5F0;
--ink:#1a1a1a;
--ink-soft:#4a4a4a;
--line:#1a1a1a;
--red:#B3261E;
--green:#1E6B3C;
--blue:#1B4B91;
--yellow:#C9971C;
}

.stApp{
background-color: var(--paper);
color: var(--ink);
}

/* Hide default streamlit chrome */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.block-container{
padding-top: 1rem;
padding-bottom: 3rem;
max-width: 1200px;
}

h1,h2,h3,h4, .masthead, .headline{
font-family: 'Playfair Display', Georgia, serif !important;
color: var(--ink) !important;
}

p, div, span, li, label{
font-family: 'Merriweather', 'Old Standard TT', Georgia, serif;
}

/* ---------------- MASTHEAD ---------------- */
.masthead-wrap{
text-align:center;
padding: 6px 0 2px 0;
}
.masthead-date{
font-family:'Merriweather', serif;
font-size:0.78rem;
letter-spacing:2px;
text-transform:uppercase;
color: var(--ink-soft);
margin-bottom: 4px;
}
.masthead{
font-size: 4.2rem;
font-weight:900;
letter-spacing: 2px;
margin: 0;
line-height:1.05;
}
.masthead-sub{
font-family:'Old Standard TT', serif;
font-style: italic;
font-size: 1.05rem;
color: var(--ink-soft);
letter-spacing: 1px;
margin-top: 2px;
}

.rule-thick{
border: none;
border-top: 4px solid var(--line);
margin: 10px 0 4px 0;
}
.rule-thin{
border: none;
border-top: 1.5px solid var(--line);
margin: 4px 0 10px 0;
}
.rule-mid{
border:none;
border-top: 1px solid #ccc4b8;
margin: 14px 0;
}

/* ---------------- NAV BAR ---------------- */
.navbar{
display:flex;
justify-content:center;
gap: 46px;
padding: 8px 0;
font-family:'Playfair Display', serif;
font-weight:700;
letter-spacing:1.5px;
text-transform:uppercase;
font-size:0.92rem;
}
.navbar span{
padding-bottom:4px;
border-bottom: 2px solid transparent;
cursor:default;
}
.navbar span:hover{
border-bottom: 2px solid var(--red);
color: var(--red);
}

/* ---------------- BREAKING BAR ---------------- */
.breaking-bar{
background: var(--red);
color: #fff;
padding: 9px 18px;
font-family:'Merriweather', serif;
font-weight:700;
font-size:0.92rem;
letter-spacing:0.5px;
border-radius: 3px;
display:flex;
align-items:center;
gap:10px;
margin: 10px 0 18px 0;
}
.breaking-tag{
background:#fff;
color: var(--red);
font-family:'Playfair Display', serif;
font-weight:900;
padding: 2px 10px;
border-radius: 2px;
font-size:0.78rem;
letter-spacing:1px;
}

/* ---------------- FEATURED HEADLINE ---------------- */
.featured-kicker{
color: var(--blue);
font-weight:700;
letter-spacing:2px;
text-transform:uppercase;
font-size:0.78rem;
margin-bottom:6px;
}
.featured-title{
font-size: 2.6rem;
font-weight:800;
line-height:1.15;
margin: 0 0 10px 0;
}
.featured-desc{
font-size:1.05rem;
color: var(--ink-soft);
line-height:1.6;
border-left: 3px solid var(--ink);
padding-left: 14px;
}
.img-placeholder{
background: repeating-linear-gradient(45deg, #e8e3d8, #e8e3d8 10px, #ded8ca 10px, #ded8ca 20px);
border: 1px solid #c9c2b2;
display:flex;
align-items:center;
justify-content:center;
color: var(--ink-soft);
font-family:'Merriweather', serif;
font-style: italic;
font-size: 0.95rem;
border-radius: 2px;
}

/* ---------------- COLUMN HEADERS ---------------- */
.col-header{
font-family:'Playfair Display', serif;
font-weight:800;
font-size:1.15rem;
text-transform:uppercase;
letter-spacing:1px;
border-bottom: 3px solid var(--ink);
padding-bottom:6px;
margin-bottom:14px;
}

/* ---------------- NEWS CARD ---------------- */
.news-card{
padding: 12px 4px 16px 4px;
border-bottom: 1px solid #d8d2c4;
margin-bottom: 6px;
transition: background 0.15s ease;
}
.news-card:hover{
background: #efeadf;
}
.news-card-title{
font-family:'Playfair Display', serif;
font-weight:700;
font-size:1.05rem;
line-height:1.3;
margin-bottom:6px;
color: var(--ink);
}
.news-card-desc{
font-size:0.88rem;
color: var(--ink-soft);
line-height:1.5;
margin-bottom:8px;
}

.badge{
display:inline-block;
font-family:'Merriweather', serif;
font-weight:700;
font-size:0.72rem;
letter-spacing:0.5px;
padding: 3px 10px;
border-radius: 12px;
text-transform:uppercase;
}
.badge-fake{ background:#fbe4e2; color: var(--red); border:1px solid var(--red);}
.badge-real{ background:#e1f0e5; color: var(--green); border:1px solid var(--green);}
.badge-suspicious{ background:#faf1dc; color: var(--yellow); border:1px solid var(--yellow);}

/* ---------------- ALERT / TRENDING ITEM ---------------- */
.alert-item{
background:#fff;
border-left: 4px solid var(--red);
padding: 10px 12px;
margin-bottom: 10px;
border-radius: 2px;
box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.trend-item{
display:flex;
justify-content:space-between;
padding: 8px 0;
border-bottom: 1px dashed #cfc8ba;
font-size:0.9rem;
}

/* ---------------- AI ANALYZER ---------------- */
.ai-section{
background: #EFF4FB;
border: 1.5px solid var(--blue);
border-radius: 6px;
padding: 26px 28px;
margin: 10px 0 26px 0;
}
.ai-title{
font-family:'Playfair Display', serif;
font-weight:800;
font-size:1.5rem;
color: var(--blue);
margin-bottom: 4px;
}
.ai-sub{
color: var(--ink-soft);
font-size:0.92rem;
margin-bottom: 18px;
}

.result-box{
background:#fff;
border-radius:6px;
padding: 16px;
text-align:center;
border: 1px solid #dcdcdc;
}
.result-label{
font-size:0.78rem;
text-transform:uppercase;
letter-spacing:1px;
color: var(--ink-soft);
margin-bottom:6px;
}
.result-value{
font-family:'Playfair Display', serif;
font-weight:800;
font-size:1.5rem;
}

/* ---------------- FOOTER ---------------- */
.footer{
text-align:center;
padding-top: 24px;
color: var(--ink-soft);
font-size:0.8rem;
letter-spacing:0.5px;
}

/* Buttons */
div.stButton > button{
background: var(--ink);
color: #fff;
font-family:'Playfair Display', serif;
font-weight:700;
letter-spacing:1px;
text-transform:uppercase;
border-radius:3px;
border: none;
padding: 8px 26px;
}
div.stButton > button:hover{
background: var(--red);
color:#fff;
}

/* Section label small caps */
.section-tag{
display:inline-block;
background: var(--ink);
color:#fff;
font-size:0.7rem;
letter-spacing:1.5px;
text-transform:uppercase;
padding:3px 10px;
margin-bottom:10px;
font-family:'Merriweather', serif;
}

/* dataframe tweak */
.stDataFrame{
border: 1px solid #1a1a1a;
}

/* ---------------- AI ANALYZER v2 ---------------- */
.analyzer-card{
background:#fff;
border:1px solid #d8d2c4;
border-radius:8px;
padding: 20px 22px;
height:100%;
}
.analyzer-card-title{
font-family:'Playfair Display', serif;
font-weight:800;
font-size:1rem;
text-transform:uppercase;
letter-spacing:1px;
color: var(--ink);
margin-bottom: 12px;
display:flex;
align-items:center;
gap:8px;
}
.example-chip-row{
display:flex;
flex-wrap:wrap;
gap:8px;
margin: 10px 0 4px 0;
}
.example-chip{
background:#EFEADF;
border:1px solid #cfc8ba;
border-radius: 14px;
padding: 4px 12px;
font-size:0.76rem;
color: var(--ink-soft);
font-family:'Merriweather', serif;
}
.example-label{
font-size:0.74rem;
letter-spacing:1px;
text-transform:uppercase;
color: var(--ink-soft);
margin-top:14px;
}

/* verdict / stamp card */
.verdict-card{
background:#fff;
border:1px solid #d8d2c4;
border-radius:8px;
padding: 20px 24px 22px 24px;
height:100%;
}
.verdict-title{
font-family:'Playfair Display', serif;
font-weight:800;
font-size:1rem;
text-transform:uppercase;
letter-spacing:1px;
margin-bottom: 14px;
display:flex;
justify-content:space-between;
align-items:center;
}
.verdict-badge-pill{
font-size:0.68rem;
background:#F0F0F0;
color: var(--ink-soft);
padding:2px 9px;
border-radius:10px;
letter-spacing:0.5px;
}
.stamp-wrap{
display:flex;
justify-content:center;
margin: 6px 0 18px 0;
}
.stamp{
width: 128px;
height: 128px;
border-radius: 50%;
border: 3px double var(--red);
color: var(--red);
display:flex;
flex-direction:column;
align-items:center;
justify-content:center;
transform: rotate(-9deg);
text-align:center;
font-family:'Playfair Display', serif;
box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
.stamp-line1{
font-size:0.6rem;
letter-spacing:1.5px;
font-weight:700;
margin-bottom:4px;
}
.stamp-line2{
font-size:1.35rem;
font-weight:900;
line-height:1.1;
}
.stamp-line3{
font-size:0.55rem;
letter-spacing:1.5px;
margin-top:4px;
font-weight:700;
}

.meter-block{ margin-bottom:14px; }
.meter-label{
display:flex;
justify-content:space-between;
font-size:0.82rem;
font-weight:700;
margin-bottom:5px;
color: var(--ink);
}
.meter-track{
width:100%;
height:9px;
background:#eee8da;
border-radius:5px;
overflow:hidden;
border:1px solid #d8d2c4;
}
.meter-fill{
height:100%;
border-radius:5px;
}

.breakdown-title{
font-size:0.72rem;
text-transform:uppercase;
letter-spacing:1px;
color: var(--ink-soft);
margin: 16px 0 10px 0;
border-top: 1px dashed #cfc8ba;
padding-top:12px;
}
.metric-row{
display:flex;
align-items:center;
gap:10px;
margin-bottom:8px;
font-size:0.78rem;
}
.metric-name{
width: 118px;
flex-shrink:0;
color: var(--ink-soft);
}
.metric-track{
flex-grow:1;
height:6px;
background:#eee8da;
border-radius:4px;
overflow:hidden;
border:1px solid #d8d2c4;
}
.metric-fill{
height:100%;
border-radius:4px;
}
.metric-pct{
width:34px;
text-align:right;
font-weight:700;
flex-shrink:0;
}

.recent-strip{
margin-top:6px;
}
.recent-item{
display:flex;
justify-content:space-between;
align-items:center;
padding: 9px 4px;
border-bottom: 1px dashed #cfc8ba;
font-size:0.85rem;
}
.recent-item span.recent-title{
color: var(--ink);
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HEADER / MASTHEAD
# ==============================================================================
st.markdown("""
<div class="masthead-wrap">
<div class="masthead-date">Saturday, August 8 2026 &nbsp;•&nbsp; Digital Edition &nbsp;•&nbsp; Powered by AI</div>
<div class="masthead">SATYARAKSHAK TIMES</div>
<div class="masthead-sub">"Truth Behind the News"</div>
</div>
<hr class="rule-thick">
<div class="navbar">
<span>🏠 Home</span>
<span>🤖 Analyze News</span>
<span>📊 Reports</span>
<span>🕵️ Users</span>
</div>
<hr class="rule-thin">
""", unsafe_allow_html=True)

# ==============================================================================
# BREAKING NEWS BAR
# ==============================================================================
st.markdown("""
<div class="breaking-bar">
<span class="breaking-tag">BREAKING</span>
<span>⚠️ AI detected a coordinated fake news campaign spreading across 3 regional networks — investigation ongoing.</span>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# FEATURED HEADLINE (FULL WIDTH)
# ==============================================================================
feat_col1, feat_col2 = st.columns([1.3, 1])

with feat_col1:
    st.markdown("""
<div class="featured-kicker">🤖 AI Investigation &nbsp;|&nbsp; Top Story</div>
<div class="featured-title">Viral "Miracle Cure" Post Traced to Bot Network Operating in Five States</div>
<div class="featured-desc">
SatyaRakshak AI's detection engine flagged an unusual spike in near-identical posts sharing
unverified health claims. Cross-referencing account creation timestamps and posting cadence,
analysts identified a coordinated network exhibiting classic bot-like behavior. The story is
developing — follow along for verified updates as the newsroom's AI systems continue tracking
the spread in real time.
</div>
""", unsafe_allow_html=True)

with feat_col2:
    st.markdown("""
<div class="img-placeholder" style="height:230px;">
📷 Featured Image Placeholder
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="rule-mid">', unsafe_allow_html=True)

# ==============================================================================
# 3-COLUMN LAYOUT: LEFT (small articles) | CENTER (main article) | RIGHT (trending/alerts)
# ==============================================================================
left_col, center_col, right_col = st.columns([1, 1.4, 1])

# ---------- LEFT COLUMN: Small News Articles ----------
with left_col:
    st.markdown('<div class="col-header">📰 More Stories</div>', unsafe_allow_html=True)

    small_articles = [
        {
            "title": "Election Rumor Debunked Within Hours by AI Fact-Checker",
            "desc": "A viral claim about polling station closures was flagged and verified as false within minutes of trending.",
            "tag": "real",
        },
        {
            "title": "Deepfake Video of Celebrity Endorsement Circulating on Social Media",
            "desc": "Video forensics detected frame-level inconsistencies typical of AI-generated synthetic media.",
            "tag": "fake",
        },
        {
            "title": "Unverified Market Crash Warning Sparks Panic Selling",
            "desc": "Source credibility score remains low; claim currently under manual review by moderators.",
            "tag": "suspicious",
        },
        {
            "title": "Local News Outlet Confirms Community Fundraiser Details",
            "desc": "Cross-checked against three independent sources and official municipal records.",
            "tag": "real",
        },
    ]

    badge_map = {
        "fake": ('<span class="badge badge-fake">🔴 Fake</span>'),
        "real": ('<span class="badge badge-real">🟢 Real</span>'),
        "suspicious": ('<span class="badge badge-suspicious">🟡 Suspicious</span>'),
    }

    for art in small_articles:
        st.markdown(f"""
<div class="news-card">
<div class="news-card-title">{art['title']}</div>
<div class="news-card-desc">{art['desc']}</div>
{badge_map[art['tag']]}
</div>
""", unsafe_allow_html=True)

# ---------- CENTER COLUMN: Main Featured Article ----------
with center_col:
    st.markdown('<div class="col-header">🔎 In-Depth Feature</div>', unsafe_allow_html=True)

    st.markdown("""
<div class="img-placeholder" style="height:180px; margin-bottom:14px;">
📷 Article Image Placeholder
</div>
<div class="news-card-title" style="font-size:1.3rem;">
Inside the Newsroom: How SatyaRakshak AI Scores Every Headline
</div>
<div class="news-card-desc" style="font-size:0.95rem;">
A behind-the-scenes look at how our verification pipeline evaluates language patterns,
source credibility, propagation speed, and network behavior to assign a real-time
trust score to breaking stories — before they reach your feed.
</div>
<span class="badge badge-real">🟢 Verified Report</span>
""", unsafe_allow_html=True)

    st.markdown('<hr class="rule-mid">', unsafe_allow_html=True)

    st.markdown("""
<div class="news-card-title" style="font-size:1.1rem;">
Op-Ed: Why Media Literacy Matters More Than Ever
</div>
<div class="news-card-desc">
As synthetic content becomes harder to distinguish from reality, experts argue that
public education on source verification is the strongest long-term defense.
</div>
<span class="badge badge-suspicious">🟡 Opinion</span>
""", unsafe_allow_html=True)

# ---------- RIGHT COLUMN: Trending / Alerts ----------
with right_col:
    st.markdown('<div class="col-header">🚨 Live Alerts</div>', unsafe_allow_html=True)

    st.markdown("""
<div class="alert-item">
<b>High Risk</b><br>
<span style="font-size:0.85rem;">Coordinated posting pattern detected on 3 accounts — Risk Score 92</span>
</div>
<div class="alert-item" style="border-left-color: var(--yellow);">
<b>Under Review</b><br>
<span style="font-size:0.85rem;">Unverified claim about school closures gaining traction</span>
</div>
<div class="alert-item" style="border-left-color: var(--green);">
<b>Resolved</b><br>
<span style="font-size:0.85rem;">Flood warning rumor confirmed false and retracted</span>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="col-header" style="margin-top:20px;">📈 Trending Topics</div>', unsafe_allow_html=True)

    trending = [
        ("#ElectionWatch2026", "🔺 +240%"),
        ("#DeepfakeAlert", "🔺 +180%"),
        ("#FactCheckIndia", "🔺 +95%"),
        ("#MarketRumor", "🔻 -12%"),
    ]
    for topic, change in trending:
        st.markdown(f"""<div class="trend-item">
<span>{topic}</span>
<span>{change}</span>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="rule-mid">', unsafe_allow_html=True)

# ==============================================================================
# AI NEWS ANALYZER SECTION
# ==============================================================================
st.markdown('<div class="section-tag">Interactive Tool</div>', unsafe_allow_html=True)
st.markdown("""
<div class="ai-title">🤖 AI News Analyzer</div>
<div class="ai-sub">Paste a headline, tweet, or article snippet below and the verification desk will generate a trust report.</div>
""", unsafe_allow_html=True)

input_col, verdict_col = st.columns([1.15, 1], gap="medium")

# ---------- LEFT: SUBMISSION PANEL ----------
with input_col:
    st.markdown('<div class="analyzer-card">', unsafe_allow_html=True)
    st.markdown('<div class="analyzer-card-title">📝 Submit Content for Verification</div>', unsafe_allow_html=True)

    news_input = st.text_area(
        "Enter news text to analyze",
        placeholder="Paste a news headline, tweet, or article excerpt here...",
        height=150,
        label_visibility="collapsed",
    )

    st.markdown('<div class="example-label">Try an example</div>', unsafe_allow_html=True)
    st.markdown("""<div class="example-chip-row">
<span class="example-chip">🧪 "Scientists confirm miracle cure..."</span>
<span class="example-chip">🗳️ "Polling stations shut early..."</span>
<span class="example-chip">📉 "Bank collapse imminent..."</span>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    analyze_clicked = st.button("🔍 Analyze Now")
    st.markdown(
        "<div style='font-size:0.72rem; color:var(--ink-soft); margin-top:8px;'>"
        "* Demo UI only — analysis shown is sample output, not a live result.</div>",
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- RIGHT: VERDICT / TRUST REPORT PANEL ----------
with verdict_col:
    st.markdown("""<div class="verdict-card">
<div class="verdict-title">
<span>🧾 Trust Report</span>
<span class="verdict-badge-pill">Sample Output</span>
</div>
<div class="stamp-wrap">
<div class="stamp">
<span class="stamp-line1">SATYARAKSHAK AI</span>
<span class="stamp-line2">🔴 FAKE</span>
<span class="stamp-line3">FLAGGED CONTENT</span>
</div>
</div>
<div class="meter-block">
<div class="meter-label"><span>Confidence Score</span><span>87.4%</span></div>
<div class="meter-track"><div class="meter-fill" style="width:87.4%; background:var(--blue);"></div></div>
</div>
<div class="meter-block">
<div class="meter-label"><span>⚠️ Risk Level</span><span>High</span></div>
<div class="meter-track"><div class="meter-fill" style="width:82%; background:var(--red);"></div></div>
</div>
<div class="breakdown-title">Signal Breakdown</div>
<div class="metric-row">
<span class="metric-name">Source Credibility</span>
<div class="metric-track"><div class="metric-fill" style="width:21%; background:var(--red);"></div></div>
<span class="metric-pct">21%</span>
</div>
<div class="metric-row">
<span class="metric-name">Language Pattern</span>
<div class="metric-track"><div class="metric-fill" style="width:74%; background:var(--yellow);"></div></div>
<span class="metric-pct">74%</span>
</div>
<div class="metric-row">
<span class="metric-name">Propagation Speed</span>
<div class="metric-track"><div class="metric-fill" style="width:91%; background:var(--red);"></div></div>
<span class="metric-pct">91%</span>
</div>
<div class="metric-row">
<span class="metric-name">Network Similarity</span>
<div class="metric-track"><div class="metric-fill" style="width:68%; background:var(--yellow);"></div></div>
<span class="metric-pct">68%</span>
</div>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

# ---------- RECENTLY ANALYZED STRIP ----------
st.markdown('<div class="analyzer-card-title" style="margin-top:4px;">🕒 Recently Analyzed</div>', unsafe_allow_html=True)
st.markdown("""<div class="recent-strip">
<div class="recent-item">
<span class="recent-title">"Government announces surprise currency change overnight"</span>
<span class="badge badge-fake">🔴 Fake</span>
</div>
<div class="recent-item">
<span class="recent-title">"City council approves new metro line extension"</span>
<span class="badge badge-real">🟢 Real</span>
</div>
<div class="recent-item">
<span class="recent-title">"Viral post claims water shortage starting next week"</span>
<span class="badge badge-suspicious">🟡 Suspicious</span>
</div>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="rule-mid">', unsafe_allow_html=True)

# ==============================================================================
# USERS / INVESTIGATION SECTION
# ==============================================================================
st.markdown('<div class="section-tag">Newsroom Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="col-header">🕵️ User Investigation Board</div>', unsafe_allow_html=True)

import pandas as pd

users_data = pd.DataFrame([
    {"Username": "@newsWatcher_21", "Activity Level": "Very High", "Risk Score": 91, "Status": "🔴 Suspicious"},
    {"Username": "@dailyTruthSeeker", "Activity Level": "Moderate", "Risk Score": 34, "Status": "🟢 Normal"},
    {"Username": "@viral_updates_now", "Activity Level": "Very High", "Risk Score": 88, "Status": "🔴 Suspicious"},
    {"Username": "@ravi.reports", "Activity Level": "Low", "Risk Score": 12, "Status": "🟢 Normal"},
    {"Username": "@breakingIN_official", "Activity Level": "High", "Risk Score": 63, "Status": "🟡 Suspicious"},
    {"Username": "@localCitizenPune", "Activity Level": "Low", "Risk Score": 8, "Status": "🟢 Normal"},
    {"Username": "@trendBot_9284", "Activity Level": "Very High", "Risk Score": 97, "Status": "🔴 Suspicious"},
])

st.dataframe(
    users_data,
    use_container_width=True,
    hide_index=True,
    height=290,
)

st.markdown("""
<div style="font-size:0.8rem; color:var(--ink-soft); margin-top:8px;">
Showing 7 of 1,204 monitored accounts &nbsp;•&nbsp; Data refreshed for UI demonstration only
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="rule-mid">', unsafe_allow_html=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
<div class="footer">
<hr class="rule-thin">
<b>SATYARAKSHAK TIMES</b> &nbsp;•&nbsp; "Truth Behind the News"<br>
A UI concept for AI-powered misinformation detection &nbsp;•&nbsp; © 2026 &nbsp;•&nbsp; All content shown is placeholder / demo data
</div>
""", unsafe_allow_html=True)