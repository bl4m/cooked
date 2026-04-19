"""
OVERTHRONE :: app.py
Entry point. Only handles page config and routing.
Run: streamlit run app.py
Requires: pip install streamlit supabase
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ───────────────
st.set_page_config(
    page_title="Overthrone · War Room",
    page_icon="⚔",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Router ───────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    restored_user = st.query_params.get("user")
    if restored_user:
        from db import get_user
        restored = get_user(restored_user)
        if restored:
            st.session_state.logged_in = True
            st.session_state.username = restored_user
            st.session_state.user_data = restored

if st.query_params.get("admin") == "true":
    from _pages.admin import show_admin_page
    show_admin_page()
    st.stop()

if not st.session_state.logged_in:
    from _pages.auth import show_auth_page
    show_auth_page()

else:
    from db import get_user
    user = get_user(st.session_state.username)

    if not user or not user.get("team"):
        from _pages.team_select import show_team_page
        show_team_page()
    else:
        st.session_state.user_data = user
        from _pages.war_room import show_war_room
        show_war_room()
