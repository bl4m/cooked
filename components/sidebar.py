"""
OVERTHRONE :: components/sidebar.py
Premium sidebar: identity, biometrics, epoch timer, quick actions.
"""

import streamlit as st
from db import push_ev, reset_gs, save_gs, load_teams_meta, load_users, simulate_epoch
from config import TEAM_COLORS, STARTING_HP


def render_sidebar(gs, tc, dn, MT, my_hp, my_ap, my_terr,
                   mins_left, secs_left, pct_left, redis_live):
    MY_COLOR = TEAM_COLORS[MT]["color"]
    hp_pct   = max(0.0, my_hp / STARTING_HP)
    ap_pct   = min(my_ap / 3000, 1.0)
    hp_col   = "#FF2244" if my_hp < 1500 else ("#FFB800" if my_hp < 3000 else MY_COLOR)

    with st.sidebar:
        # ── Brand ─────────────────────────────────────────────
        st.markdown("""
        <div class="sb-head">
            <div style="font-family:'Orbitron',monospace;font-size:1.05rem;font-weight:900;
                letter-spacing:5px;background:linear-gradient(135deg,#8a6010,#FFD700,#D4AF37);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                OVERTHRONE
            </div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.5rem;
                color:#2a2a45;letter-spacing:3px;margin-top:4px">
                HELIX × ISTE · WAR ROOM OS v5
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Sovereign Identity ────────────────────────────────
        teams_meta   = load_teams_meta()
        my_meta      = teams_meta.get(MT, {})
        members      = my_meta.get("members", [st.session_state.username])
        all_users    = load_users()
        member_names = [all_users.get(m, {}).get("display_name", m) for m in members]
        pills = "".join(f'<span class="member-pill">{n}</span>' for n in member_names)

        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-title">SOVEREIGN IDENTITY</div>
            <div class="sb-row">
                <span class="sb-lbl">HANDLE</span>
                <span class="sb-val" style="color:{MY_COLOR}">{dn}</span>
            </div>
            <div class="sb-row">
                <span class="sb-lbl">KINGDOM</span>
                <span class="sb-val" style="color:{MY_COLOR}">{TEAM_COLORS[MT]['icon']} {MT}</span>
            </div>
        </div>
        <div class="sb-section">
            <div class="sb-title">TEAM ROSTER</div>
            {pills}
        </div>
        """, unsafe_allow_html=True)

        # ── Biometrics ────────────────────────────────────────
        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-title">COMBAT METRICS · LIVE</div>
            <div class="sb-row">
                <span class="sb-lbl">HEALTH</span>
                <span class="sb-val" style="color:{hp_col}">{my_hp:,} HP</span>
            </div>
            <div class="mini-bar" style="margin-bottom:10px">
                <div class="mini-bar-f" style="width:{hp_pct*100:.0f}%;background:{hp_col};box-shadow:0 0 6px {hp_col}88"></div>
            </div>
            <div class="sb-row">
                <span class="sb-lbl">ATTACK PTS</span>
                <span class="sb-val" style="color:#00E5FF">{my_ap:,} AP</span>
            </div>
            <div class="mini-bar" style="margin-bottom:10px">
                <div class="mini-bar-f" style="width:{ap_pct*100:.0f}%;background:#00E5FF;box-shadow:0 0 5px #00E5FF66"></div>
            </div>
            <div class="sb-row">
                <span class="sb-lbl">TERRITORY</span>
                <span class="sb-val" style="color:#D4AF37">{my_terr} / 100</span>
            </div>
            <div class="mini-bar">
                <div class="mini-bar-f" style="width:{my_terr}%;background:linear-gradient(90deg,#D4AF37,#FFD700)"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Alliance Status ────────────────────────────────────
        alliances = gs.get("alliances", {}).get(MT, [])
        ally_color = TEAM_COLORS.get(alliances[0], {}).get("color", "#00CC88") if alliances else "#666666"
        ally_icon = TEAM_COLORS.get(alliances[0], {}).get("icon", "·") if alliances else "·"
        ally_text = f"{ally_icon} {alliances[0]}" if alliances else "NONE"
        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-title">ALLIANCE STATUS</div>
            <div class="sb-row">
                <span class="sb-lbl">ALLIED WITH</span>
                <span class="sb-val" style="color:{ally_color}">{ally_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Epoch ─────────────────────────────────────────────
        timer_color = "#FF2244" if mins_left < 3 else ("#FFB800" if mins_left < 7 else "#FFD700")
        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-title">EPOCH STATUS</div>
            <div class="sb-row">
                <span class="sb-lbl">EPOCH #</span>
                <span class="sb-val" style="color:#D4AF37;font-weight:700">{gs['epoch']}</span>
            </div>
            <div class="sb-row">
                <span class="sb-lbl">PHASE</span>
                <span class="sb-val" style="color:#00E5FF;font-size:0.58rem;letter-spacing:1px">{gs['phase']}</span>
            </div>
            <div class="sb-row" style="margin-top:6px">
                <span class="sb-lbl">REMAINING</span>
                <span style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;
                    color:{timer_color};filter:drop-shadow(0 0 6px {timer_color}55)">
                    {mins_left:02d}:{secs_left:02d}
                </span>
            </div>
            <div class="mini-bar" style="margin-top:8px">
                <div class="mini-bar-f" style="width:{pct_left*100:.0f}%;
                    background:linear-gradient(90deg,{timer_color},{timer_color}aa)"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Quick Actions ─────────────────────────────────────
        st.markdown('<div class="sb-section"><div class="sb-title">QUICK ACTIONS</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="small")
        with col1:
            if st.button("⚡ EPOCH", use_container_width=True, help="Simulate epoch"):
                new_gs = simulate_epoch(gs)
                save_gs(new_gs)
                push_ev("SYS", f"Epoch {new_gs['epoch']} begins")
                st.rerun()
        with col2:
            if st.button("↺ RESET", use_container_width=True, help="Reset entire game"):
                reset_gs()
                push_ev("SYS", "Game reset — new epoch begins")
                st.rerun()
        if st.button("⟳  REFRESH DATA", use_container_width=True):
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── System Status ─────────────────────────────────────
        r_col = "#00CC88" if redis_live else "#FF2244"
        r_txt = "● CONNECTED" if redis_live else "● IN-MEMORY (RUN SQL SETUP)"
        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-title">SYSTEM STATUS</div>
            <div class="sb-row">
                <span class="sb-lbl">SUPABASE</span>
                <span style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:{r_col}">{r_txt}</span>
            </div>
            <div class="sb-row">
                <span class="sb-lbl">WEBSOCKET</span>
                <span style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#00E5FF">● :8765</span>
            </div>
            <div class="sb-row">
                <span class="sb-lbl">PARTICIPANTS</span>
                <span style="font-family:'Orbitron',monospace;font-size:0.65rem;color:#D4AF37">200</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Logout ────────────────────────────────────────────
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("⬡  LOGOUT", use_container_width=True):
            for k in ["logged_in", "username", "user_data", "active_tab",
                      "ws_log", "seeded", "code_outputs"]:
                st.session_state.pop(k, None)
            for k in ["user", "tab", "admin"]:
                st.query_params.pop(k, None)
            st.rerun()
