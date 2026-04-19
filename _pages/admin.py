"""
OVERTHRONE :: _pages/admin.py
Game Master / Admin utility for managing players, game state, and world data.
"""
import streamlit as st
import json
from db import R, load_users, load_gs, load_teams, save_gs, hash_pw
from config import STARTING_HP, STARTING_AP
from styles.theme import get_auth_css

def show_admin_page():
    st.markdown(get_auth_css(), unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-bottom:1.5rem; text-align:center;">
        <div style="font-family:'Orbitron',monospace;font-size:1.8rem;font-weight:900;
            letter-spacing:5px;color:#FF2244;margin-bottom:6px">OVERTHRONE : GAME MASTER</div>
        <div style="font-family:'Rajdhani',sans-serif;font-size:0.9rem;color:#dde0f5">
            Full World Administration Panel
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECURITY GATE ───────────────────────────────────────────
    if not st.session_state.get("admin_unlocked", False):
        with st.container():
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                pwd = st.text_input("Enter Game Master Password", type="password", key="admin_pwd")
                if st.button("AUTHENTICATE", use_container_width=True):
                    if pwd == "overlord":
                        st.session_state.admin_unlocked = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED.")
        return

    # ── ADMIN TABS ───────────────────────────────────────────────
    admin_mode = st.radio("Select Section", ["👥 Players", "🌍 Game State", "🗺️ Territories", "⚙️ Danger Zone"], horizontal=True)
    
    # TAB 1: PLAYER MANAGEMENT
    if admin_mode == "👥 Players":
        st.markdown("### 👥 PLAYER MANAGEMENT")
        try:
            users = load_users()
            if not users:
                st.info("No players registered yet.")
            else:
                for username, user_data in users.items():
                    with st.expander(f"👤 {username}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Account Info**")
                            display_name = user_data.get("display_name", "")
                            new_display_name = st.text_input("Display Name", value=display_name, key=f"dn_{username}")
                            
                            if st.checkbox("Change Password", key=f"pwd_check_{username}"):
                                new_pwd = st.text_input("New Password", type="password", key=f"pwd_new_{username}")
                                if st.button("Update Password", key=f"pwd_btn_{username}"):
                                    users[username]["pw_hash"] = hash_pw(new_pwd)
                                    R.set("ot:users", json.dumps(users))
                                    st.success("✅ Password updated!")
                        
                        with col2:
                            st.markdown("**Team Assignment**")
                            teams = load_teams()
                            team_list = list(teams.keys()) if teams else []
                            team_options = ["-- Unassigned --"] + team_list
                            current_team = user_data.get("team") or "-- Unassigned --"
                            
                            idx = team_options.index(current_team) if current_team in team_options else 0
                            new_team = st.selectbox("Team", team_options, index=idx, key=f"team_{username}")
                            
                            if st.button("Save", key=f"team_btn_{username}"):
                                users[username]["team"] = new_team if new_team != "-- Unassigned --" else None
                                users[username]["display_name"] = new_display_name
                                R.set("ot:users", json.dumps(users))
                                st.success("✅ Updated!")
                                st.rerun()
                        
                        st.divider()
                        st.caption(f"Created: {user_data.get('created', 'N/A')} | Team: {user_data.get('team', 'None')}")
        except Exception as e:
            st.error(f"Error loading players: {str(e)}")
    
    # TAB 2: GAME STATE
    elif admin_mode == "🌍 Game State":
        st.markdown("### 🌍 GAME STATE")
        try:
            gs = load_gs()
            teams = load_teams()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Epoch**")
                new_epoch = st.number_input("Number", value=gs.get("epoch", 1), min_value=1, key="epoch_edit")
                if st.button("Update", key="epoch_btn"):
                    gs["epoch"] = int(new_epoch)
                    save_gs(gs)
                    st.success("✅ Updated!")
            
            with col2:
                st.markdown("**Phase**")
                phases = ["PREPARATION", "BATTLES", "RESOLUTION"]
                current = gs.get("phase", "PREPARATION")
                idx = phases.index(current) if current in phases else 0
                new_phase = st.selectbox("Select", phases, index=idx, key="phase_sel")
                if st.button("Update", key="phase_btn"):
                    gs["phase"] = new_phase
                    save_gs(gs)
                    st.success("✅ Updated!")
            
            with col3:
                st.markdown("**End Time**")
                epoch_end = gs.get("epoch_end", "")
                new_epoch_end = st.text_input("ISO", value=epoch_end, key="epoch_end_edit")
                if st.button("Update", key="epoch_end_btn"):
                    gs["epoch_end"] = new_epoch_end
                    save_gs(gs)
                    st.success("✅ Updated!")
            
            st.divider()
            st.markdown("**Team Stats**")
            
            for team_name in teams.keys():
                with st.expander(f"🏰 {team_name}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        hp = int(gs["hp"].get(team_name, STARTING_HP))
                        new_hp = st.number_input("HP", value=hp, min_value=0, key=f"hp_{team_name}")
                    
                    with col2:
                        ap = int(gs["ap"].get(team_name, STARTING_AP))
                        new_ap = st.number_input("AP", value=ap, min_value=0, key=f"ap_{team_name}")
                    
                    if st.button("Save", key=f"save_stats_{team_name}"):
                        gs["hp"][team_name] = int(new_hp)
                        gs["ap"][team_name] = int(new_ap)
                        save_gs(gs)
                        st.success(f"✅ {team_name} updated!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # TAB 3: TERRITORIES
    elif admin_mode == "🗺️ Territories":
        st.markdown("### 🗺️ TERRITORIES")
        try:
            gs = load_gs()
            teams = load_teams()
            
            st.markdown("**Distribution**")
            for team_name in teams.keys():
                count = sum(1 for cell in gs["grid"] if cell == team_name)
                st.write(f"{team_name}: **{count}** cells")
            
            unclaimed = sum(1 for cell in gs["grid"] if not cell)
            st.write(f"Unclaimed: **{unclaimed}** cells")
            
            st.divider()
            st.markdown("**Edit Grid**")
            
            grid_display = ",".join(str(c) if c else "." for c in gs["grid"])
            st.code(f"Cells ({len(gs['grid'])}): {grid_display}", language=None)
            
            cell_idx = st.number_input("Cell Index", min_value=0, max_value=len(gs["grid"])-1, key="cell_edit_idx")
            
            team_list = list(teams.keys()) if teams else []
            cell_options = ["-- Unclaim --"] + team_list
            current_owner = gs["grid"][cell_idx] or "-- Unclaim --"
            idx = cell_options.index(current_owner) if current_owner in cell_options else 0
            new_owner = st.selectbox("New Owner", cell_options, index=idx, key="cell_owner")
            
            if st.button("Update Cell", key="cell_update_btn"):
                gs["grid"][cell_idx] = new_owner if new_owner != "-- Unclaim --" else ""
                save_gs(gs)
                st.success(f"✅ Cell #{cell_idx} updated!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # TAB 4: DANGER ZONE
    else:  # admin_mode == "⚙️ Danger Zone"
        st.markdown("### ⚙️ DANGER ZONE")
        st.warning("⚠️ **IRREVERSIBLE ACTIONS** - Use with extreme caution!")
        
        st.divider()
        st.markdown("**Reset Everything**")
        if st.button("🔥 FULL DATABASE RESET", use_container_width=True):
            R.flushdb()
            st.success("☠️ DATABASE FLUSHED")
            st.session_state.admin_unlocked = False
            st.rerun()
        
        st.divider()
        if st.button("LOGOUT", use_container_width=True):
            st.session_state.admin_unlocked = False
            st.rerun()
