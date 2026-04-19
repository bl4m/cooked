"""
OVERTHRONE :: _pages/team_select.py
Dynamic team creation — players create teams with custom names.
"""
import streamlit as st
from db import get_user, load_teams, create_team, join_team, push_ev
from styles.theme import get_auth_css


def show_team_page():
    username = st.session_state.username
    user     = get_user(username)
    dn       = user.get("display_name", username) if user else username
    teams    = load_teams()

    st.markdown(get_auth_css(), unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-bottom:1.5rem">
        <div style="font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:900;
            letter-spacing:5px;color:#c9a227;margin-bottom:6px">OVERTHRONE</div>
        <div style="font-family:'Rajdhani',sans-serif;font-size:0.85rem;color:#6a70a0">
            Welcome, <strong style="color:#dde0f5">{dn}</strong> — create or join a Kingdom
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CREATE NEW TEAM ────────────────────────────────────────
    with st.expander("⚔  Create New Kingdom", expanded=not bool(teams)):
        new_name = st.text_input("Kingdom Name", placeholder="e.g., Iron Wolves", key="new_team_name")
        new_pass = st.text_input("Vault Password", type="password", key="new_team_pass")
        if st.button("Create Kingdom", use_container_width=True, key="create_team_btn"):
            if new_name.strip() and new_pass.strip():
                ok, msg = create_team(new_name.strip(), username, new_pass.strip())
                if ok:
                    push_ev("SYS", f'Kingdom "{new_name}" was founded by {dn}')
                    st.session_state.user_data = get_user(username)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Enter a valid kingdom name and password.")

    # ── JOIN EXISTING TEAM ─────────────────────────────────────
    if teams:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        with st.expander("🛡️ Join Existing Kingdom", expanded=bool(teams)):
            j_name = st.text_input("Kingdom Identity", placeholder="Exact Kingdom Name", key="join_team_name")
            j_pwd  = st.text_input("Vault Password", type="password", key="join_team_pwd")
            if st.button("Access Vault →", use_container_width=True):
                if j_name.strip() and j_pwd.strip():
                    ok, msg = join_team(j_name.strip(), username, j_pwd.strip())
                    if ok:
                        push_ev("SYS", f"{dn} bypassed security and joined {j_name}", j_name)
                        st.session_state.user_data = get_user(username)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Identity and Password required.")

    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
    if st.button("Sign out", use_container_width=False, key="logout_team"):
        for k in ["logged_in", "username", "user_data", "active_section",
                  "ws_log", "seeded", "code_outputs"]:
            st.session_state.pop(k, None)
        for k in ["user", "tab", "admin"]:
            st.query_params.pop(k, None)
        st.rerun()
