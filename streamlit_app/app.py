import os
import streamlit as st
import requests
import pandas as pd

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Trendyol Price Tracker", page_icon="🏷️", layout="wide")

st.markdown("""
<style>
    .main > div { padding: 1.5rem 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        padding: 8px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff6b35 !important;
        color: white !important;
    }
    div[data-testid="stForm"] { background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border: 1px solid #e9ecef; }
    .stButton > button {
        background-color: #ff6b35;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
    }
    .stButton > button:hover { background-color: #e55a2b !important; color: white !important; }
    .st-emotion-cache-1q7spjk { border: 1px solid #e9ecef; border-radius: 8px; }
    h1, h2, h3 { color: #212529; }
    .stSuccess { background-color: #d4edda; color: #155724; border-radius: 6px; }
    .stInfo { background-color: #d1ecf1; color: #0c5460; border-radius: 6px; }
    .stError { background-color: #f8d7da; color: #721c24; border-radius: 6px; }
    .stDataFrame { border: 1px solid #dee2e6; border-radius: 8px; }
    [data-testid="column"] { background: white; padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid #e9ecef; margin-bottom: 4px; }
    .stExpander { border: 1px solid #e9ecef; border-radius: 8px; margin-top: 8px; }
    footer { display: none; }
</style>
""", unsafe_allow_html=True)

st.title("🏷️ Trendyol Price Tracker")
st.markdown("Monitor product prices from Trendyol and get notified on changes.")

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
