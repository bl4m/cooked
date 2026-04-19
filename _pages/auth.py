"""OVERTHRONE :: _pages/auth.py"""
import streamlit as st
from db import login_user, register_user
from styles.theme import get_auth_css


def show_auth_page():
    st.markdown(get_auth_css(), unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:1.5rem">
        <div style="font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:900;
            letter-spacing:5px;color:#c9a227;margin-bottom:6px">OVERTHRONE</div>
        <div style="font-family:'Rajdhani',sans-serif;font-size:0.82rem;color:#6a70a0">
            Kingdom simulation · HELIX × ISTE event portal
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab = st.radio("Authentication mode", ["Sign In", "Register"], horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    if tab == "Sign In":
        _login()
    else:
        _register()

    st.markdown("""
    <div style="margin-top:2rem;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,0.06);
        font-size:0.7rem;color:#3a3a60;letter-spacing:1px">
        KINGDOMS RISE. KINGDOMS FALL. ⚔
    </div>
    """, unsafe_allow_html=True)


def _login():
    username = st.text_input("Username", key="login_user", placeholder="your_handle")
    password = st.text_input("Password", key="login_pw", type="password", placeholder="password")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Sign In", use_container_width=True):
        if not username or not password:
            st.warning("Fill in both fields.")
            return
        ok, result = login_user(username, password)
        if ok:
            st.session_state.logged_in  = True
            st.session_state.username   = username
            st.session_state.user_data  = result
            st.query_params["user"] = username
            st.query_params["tab"] = "Home"
            st.rerun()
        else:
            st.error(result)


def _register():
    dn  = st.text_input("Display Name", key="reg_dn", placeholder="Your Name")
    un  = st.text_input("Username",     key="reg_un", placeholder="unique_handle")
    pw  = st.text_input("Password",     key="reg_pw", type="password", placeholder="min 6 chars")
    pw2 = st.text_input("Confirm",      key="reg_c",  type="password", placeholder="repeat")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Create Account", use_container_width=True):
        if not all([dn, un, pw, pw2]):
            st.warning("Fill in all fields.")
        elif pw != pw2:
            st.error("Passwords don't match.")
        elif len(pw) < 6:
            st.error("Password must be ≥ 6 characters.")
        else:
            ok, msg = register_user(un, pw, dn)
            if ok:
                st.success(f"{msg} — sign in to continue.")
            else:
                st.error(msg)
