"""
Streamlit frontend application for Search Analytics System.
Provides UI for keyword search and result visualization.
"""

import streamlit as st
from api_client import APIClient
from datetime import datetime


class SearchAnalyticsApp:
    """Streamlit application for search analytics and synthesis visualization."""
    
    @staticmethod
    def configure_page():
        """Configures Streamlit page settings for wide layout display."""
        st.set_page_config(
            page_title="Search Analytics System",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
    
    @staticmethod
    def render_header():
        """Renders the application title and description."""
        st.title("🔍 Search Analytics & Synthesis System")
        st.write("An integrated asynchronous processing dashboard for keyword extraction and local text summaries.")
        st.write("")
    
    @staticmethod
    def render_search_input():
        """
        Renders the search input field and button.
        
        Returns:
            tuple: (keyword string, button_clicked bool).
        """
        col_input, col_btn = st.columns([0.85, 0.15], gap="small")
        
        with col_input:
            keyword = st.text_input(
                "Search Phrase Entry",
                placeholder="Enter a keyword or keyphrase to process...",
                label_visibility="collapsed"
            )
        
        with col_btn:
            search_clicked = st.button("Run Pipeline", width="stretch")
        
        return keyword, search_clicked
    
    @staticmethod
    def handle_search(keyword: str):
        """
        Executes search API call and stores result in session state.
        
        Args:
            keyword: Search term to query.
        """
        if not keyword.strip():
            st.warning("Please specify a valid search term.")
            st.stop()

        with st.spinner("Executing pipeline routines..."):
            try:
                data = APIClient.search(keyword)
                st.session_state["search_payload"] = data
                st.success("Data streams updated successfully.")
            except Exception as e:
                st.error(f"Upstream Gateway Operational Failure: {str(e)}")
    
    @staticmethod
    def render_results(data: dict):
        """
        Renders the search results with performance telemetry.
        
        Args:
            data: Search response dictionary containing results and metadata.
        """
        st.divider()
        
        active_keyword = data.get("keyword", "")
        performance_logs = data.get("performance_history", [])
        results = data.get("results", [])
        ai_summary = data.get("ai_synthesis")

        col_left, col_right = st.columns([0.45, 0.55], gap="large")
        
        with col_left:
            SearchAnalyticsApp.render_ai_synthesis(ai_summary)
            SearchAnalyticsApp.render_performance_telemetry(active_keyword, performance_logs)

        with col_right:
            SearchAnalyticsApp.render_search_results(results)
    
    @staticmethod
    def render_ai_synthesis(ai_summary: str):
        """
        Renders the AI synthesis section.
        
        Args:
            ai_summary: AI-generated summary text or None.
        """
        st.subheader("💡 AI Synthesis")
        if ai_summary:
            st.info(ai_summary)
        else:
            st.write("*No summary string generated for this context.*")
        st.write("")
        st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px dashed #CBD5E1;'>", unsafe_allow_html=True)
        st.write("")
    
    @staticmethod
    def render_performance_telemetry(active_keyword: str, performance_logs: list):
        """
        Renders the performance telemetry tracking section.
        
        Args:
            active_keyword: Current search keyword.
            performance_logs: List of performance log entries.
        """
        st.subheader("📊 Performance Telemetry Map")
        st.caption(f"Audit tracking log loops for keyword: **'{active_keyword}'**")
        st.write("")

        if not performance_logs:
            st.info("No prior telemetry records compiled for this query configuration node.")
            return

        h_col1, h_col2, h_col3 = st.columns([0.4, 0.35, 0.25])
        with h_col1: st.caption("🕒 TIMESTAMP")
        with h_col2: st.caption("⚙️ ROUTE CONTEXT")
        with h_col3: st.caption("⏱️ SPEED")
        st.markdown("<hr style='margin: 2px 0 8px 0; border: none; border-top: 1px solid #CBD5E1;'>", unsafe_allow_html=True)

        for entry in performance_logs:
            try:
                t_str = entry.get("timestamp", "").replace("Z", "+00:00")
                t_clean = datetime.fromisoformat(t_str).strftime("%H:%M:%S UTC")
            except Exception:
                t_clean = entry.get("timestamp", "Unknown")

            exec_type = entry.get("execution_type", "Unknown")
            v_id = f"v{entry.get('version', 1)}"
            t_time = entry.get("turnaround_time_seconds", 0.0)

            m_col1, m_col2, m_col3 = st.columns([0.4, 0.35, 0.25])
            with m_col1: st.markdown(f"`{t_clean}`")
            with m_col2: st.markdown(f"**{exec_type}** `({v_id})`")
            with m_col3: st.markdown(f"`{t_time:.4f}s`")
            
            st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)
        
        st.write("")
        
        if len(performance_logs) > 1:
            SearchAnalyticsApp.render_speed_metrics(performance_logs)
    
    @staticmethod
    def render_speed_metrics(performance_logs: list):
        """
        Renders speed comparison metrics between initial and latest runs.
        
        Args:
            performance_logs: List of performance log entries.
        """
        initial_run = performance_logs[0]
        latest_run = performance_logs[-1]
        
        t_initial = float(initial_run.get("turnaround_time_seconds", 0.0))
        t_latest = float(latest_run.get("turnaround_time_seconds", 0.0))
        speed_delta = max(0.0, t_initial - t_latest)
        
        met_col1, met_col2 = st.columns(2)
        with met_col1:
            st.metric("Live Sync (Initial)", f"{t_initial:.2f}s")
        with met_col2:
            st.metric("Cache Read (Latest)", f"{t_latest:.4f}s")
            
        st.caption(f"🚀 Optimized loop accelerated retrieval pipeline operations by **{speed_delta:.2f} seconds**.")
    
    @staticmethod
    def render_search_results(results: list):
        """
        Renders the primary search results section.
        
        Args:
            results: List of search result dictionaries.
        """
        st.subheader("📋 Primary Search Results")
        if not results:
            st.warning("Keyword returned zero organic results. Empty list stored safely.")
            return

        for result in results:
            rank = result.get("rank", "-")
            title = result.get("title", "Untitled Document Asset")
            url = result.get("url", "#")
            snippet = result.get("snippet", "No preview description blocks found.")
            
            with st.expander(f"**{rank}. {title}**", expanded=True):
                st.write(snippet)
                st.caption(f"📍 **Source:** `{url}`")
                st.link_button("View Document ↗", url, width="content")
                st.write("")


def main():
    """Main entry point for the Streamlit application."""
    SearchAnalyticsApp.configure_page()
    SearchAnalyticsApp.render_header()
    
    keyword, search_clicked = SearchAnalyticsApp.render_search_input()
    
    if search_clicked:
        SearchAnalyticsApp.handle_search(keyword)
    
    if "search_payload" in st.session_state:
        data = st.session_state["search_payload"]
        if data and isinstance(data, dict):
            SearchAnalyticsApp.render_results(data)


if __name__ == "__main__":
    main()
