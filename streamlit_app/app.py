import os
import streamlit as st
import requests
import pandas as pd

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Trendyol Price Tracker", page_icon="🏷️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Base & Background ── */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
    }
    .main > div {
        padding: 2rem 2.5rem;
    }

    /* ── Typography ── */
    h1 { 
        font-family: 'Inter', sans-serif !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #e6edf3 !important;
        letter-spacing: -0.5px;
        margin-bottom: 0.25rem !important;
    }
    h2 {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #8b949e !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 1.25rem !important;
    }
    h3 {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #c9d1d9 !important;
    }
    p, label, div {
        color: #c9d1d9 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #161b22;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-bottom: 1.75rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px;
        padding: 8px 22px;
        font-weight: 600;
        font-size: 0.85rem;
        color: #8b949e !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.15s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF6000 !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(255, 96, 0, 0.35);
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* ── Form Card ── */
    div[data-testid="stForm"] {
        background: #161b22 !important;
        padding: 1.75rem !important;
        border-radius: 12px !important;
        border: 1px solid #30363d !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.35);
        margin-bottom: 1.5rem;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #e6edf3 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important;
        padding: 10px 14px !important;
        transition: border-color 0.15s ease;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #FF6000 !important;
        box-shadow: 0 0 0 3px rgba(255, 96, 0, 0.15) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #484f58 !important;
    }

    /* ── Labels ── */
    .stTextInput label, .stNumberInput label {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #8b949e !important;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #FF6000 0%, #e55200 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 10px 20px !important;
        letter-spacing: 0.2px;
        transition: all 0.15s ease !important;
        box-shadow: 0 2px 8px rgba(255, 96, 0, 0.25);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff7519 0%, #FF6000 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 16px rgba(255, 96, 0, 0.4) !important;
        transform: translateY(-1px);
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* ── DataFrames ── */
    .stDataFrame {
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
        overflow: hidden;
    }
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: #161b22 !important;
    }
    iframe[title="dataframe"] {
        border-radius: 10px;
    }

    /* ── Alerts ── */
    .stSuccess, div[data-testid="stAlert"][kind="success"] {
        background-color: #0d2818 !important;
        border: 1px solid #2ea043 !important;
        border-radius: 8px !important;
        color: #3fb950 !important;
    }
    .stInfo, div[data-testid="stAlert"][kind="info"] {
        background-color: #0c1d2e !important;
        border: 1px solid #1f6feb !important;
        border-radius: 8px !important;
        color: #58a6ff !important;
    }
    .stError, div[data-testid="stAlert"][kind="error"] {
        background-color: #2d0f0f !important;
        border: 1px solid #f85149 !important;
        border-radius: 8px !important;
        color: #f85149 !important;
    }

    /* ── Query Row Cards ── */
    [data-testid="column"] {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        margin-bottom: 6px !important;
    }

    /* ── Expander ── */
    .stExpander {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
        margin-top: 12px !important;
    }
    .stExpander summary {
        font-weight: 600 !important;
        color: #c9d1d9 !important;
        font-size: 0.9rem !important;
    }
    .stExpander summary:hover {
        color: #FF6000 !important;
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: #FF6000 !important;
    }

    /* ── Divider ── */
    hr {
        border-color: #30363d !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Subheader ── */
    .stSubheader, [data-testid="stHeadingWithActionElements"] h3 {
        color: #8b949e !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }

    /* ── Markdown bold/code inside columns ── */
    strong { color: #e6edf3 !important; font-weight: 600; }
    code {
        background: #30363d !important;
        color: #79c0ff !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
    }

    /* ── Line chart ── */
    .stVegaLiteChart, [data-testid="stArrowVegaLiteChart"] {
        background: #0d1117 !important;
        border-radius: 8px !important;
    }

    /* ── Number input arrows ── */
    .stNumberInput button {
        background: #30363d !important;
        border-color: #30363d !important;
        color: #e6edf3 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    .stNumberInput button:hover {
        background: #FF6000 !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* ── Hide Streamlit chrome ── */
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    header[data-testid="stHeader"] { background: transparent !important; }

    /* ── Container wrapper for scrape section ── */
    [data-testid="stVerticalBlock"] > [data-testid="element-container"] > div[data-testid="stHorizontalBlock"] {
        gap: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
col_title, col_badge = st.columns([6, 1])
with col_title:
    st.title("🏷️ Trendyol Price Tracker")
    st.markdown(
        "<p style='color:#8b949e; margin-top:-8px; font-size:0.9rem;'>"
        "Monitor product prices from Trendyol and get notified on changes."
        "</p>",
        unsafe_allow_html=True,
    )
with col_badge:
    st.markdown(
        "<div style='text-align:right; padding-top:12px;'>"
        "<span style='background:#161b22; border:1px solid #30363d; border-radius:20px;"
        " padding:5px 12px; font-size:0.75rem; color:#8b949e; font-weight:600;'>"
        "🟢 Live</span></div>",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 Search Queries", "📦 Products", "🔄 Scrape"])

with tab1:
    st.header("Manage Search Queries")

    with st.form("add_query"):
        col_key, col_min, col_max, col_btn = st.columns([3, 1.5, 1.5, 1])
        with col_key:
            keyword = st.text_input("Search Keyword", placeholder="e.g. kulaklık")
        with col_min:
            min_price = st.number_input("Min Price (TL)", min_value=0.0, value=0.0, step=10.0)
        with col_max:
            max_price = st.number_input("Max Price (TL)", min_value=0.0, value=0.0, step=10.0)
        with col_btn:
            st.write("")
            st.write("")
            submitted = st.form_submit_button("Add Query", use_container_width=True)

        if submitted and keyword:
            payload = {"keyword": keyword}
            if min_price > 0:
                payload["min_price"] = min_price
            if max_price > 0:
                payload["max_price"] = max_price
            resp = requests.post(f"{API_URL}/search-queries", json=payload)
            if resp.ok:
                st.success(f"Added: {keyword}")
            else:
                st.error(f"Error: {resp.text}")

    resp = requests.get(f"{API_URL}/search-queries")
    if resp.ok:
        queries = resp.json()
        if queries:
            st.subheader("Saved Queries")
            df = pd.DataFrame(queries)
            st.dataframe(df, use_container_width=True, hide_index=True)

            for q in queries:
                cols = st.columns([4, 1, 1])
                status_icon = "✅" if q["is_active"] else "⏸️"
                price_range = ""
                if q.get("min_price"):
                    price_range += f" ≥{q['min_price']}TL"
                if q.get("max_price"):
                    price_range += f" ≤{q['max_price']}TL"
                cols[0].markdown(f"**{q['keyword']}** {status_icon} `{q['is_active']}`{price_range}")
                if cols[1].button("Toggle", key=f"toggle_{q['id']}", use_container_width=True):
                    requests.post(f"{API_URL}/search-queries/{q['id']}/toggle")
                    st.rerun()
                if cols[2].button("Delete", key=f"del_{q['id']}", use_container_width=True):
                    requests.delete(f"{API_URL}/search-queries/{q['id']}")
                    st.rerun()
        else:
            st.info("No search queries yet. Add one above.")

with tab2:
    st.header("Tracked Products")

    resp = requests.get(f"{API_URL}/products")
    if resp.ok:
        products = resp.json()
        if products:
            df = pd.DataFrame(products)
            cols = ["title", "current_price", "currency", "last_checked"]
            st.dataframe(df[cols], use_container_width=True, hide_index=True)

            with st.expander("📈 View Price History"):
                for p in products:
                    st.markdown(f"**{p['title']}** — Current: **{p['current_price']} {p['currency']}**")
                    hist_resp = requests.get(f"{API_URL}/products/{p['id']}/history")
                    if hist_resp.ok:
                        hist = hist_resp.json()
                        if hist:
                            hist_df = pd.DataFrame(hist)
                            st.line_chart(hist_df.set_index("checked_at")["price"], height=250)
                    st.divider()
        else:
            st.info("No products tracked yet. Run a scrape to find products.")

with tab3:
    st.header("Manual Scrape")

    with st.container():
        col_kw, col_btn = st.columns([4, 1])
        with col_kw:
            keyword = st.text_input("Keyword to scrape", placeholder="e.g. kulaklık")
        with col_btn:
            st.write("")
            st.write("")
            if st.button("Scrape Now", use_container_width=True):
                if keyword:
                    with st.spinner("Scraping Trendyol..."):
                        resp = requests.post(f"{API_URL}/scrape", params={"keyword": keyword})
                    if resp.ok:
                        data = resp.json()
                        st.success(f"Found {len(data['results'])} products")
                        if data["results"]:
                            st.dataframe(pd.DataFrame(data["results"]), use_container_width=True, hide_index=True)
                    else:
                        st.error(f"Error: {resp.text}")

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("▶️ Run Daily Check Now", use_container_width=True):
            with st.spinner("Running daily check..."):
                resp = requests.post(f"{API_URL}/run-daily-check")
            if resp.ok:
                st.success("Daily check completed!")
            else:
                st.error(f"Error: {resp.text}")