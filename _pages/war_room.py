"""
OVERTHRONE :: _pages/war_room.py
Neon UI + Grid Map + Automated Attack Bot Execution
"""

import json
import time
import uuid
from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

from db import (
    load_gs, load_evs, terr_count, load_teams, load_users,
    push_ev, save_gs, reset_gs, redis_live, run_code_safe, get_user
)
from config import (
    TASKS, DIFF_COLOR, EVENT_COLORS, STARTING_HP, STARTING_AP,
    EPOCH_DURATION_SECS, ATTACK_COST_AP, CELL_COLORS, CELL_GLOW,
    TERRAIN_SPECIAL, MONARCH_TASK_PORTAL
)
from styles.theme import get_full_css


# Cache data loads for 1.5 seconds to speed up UI interactions
@st.cache_data(ttl=1.5)
def _cached_load_gs():
    return load_gs()

@st.cache_data(ttl=1.5)
def _cached_load_teams():
    return load_teams()

@st.cache_data(ttl=1.5)
def _cached_load_evs(count=40):
    return load_evs(count)

@st.cache_data(ttl=1.5)
def _cached_load_users():
    return load_users()


def _normalize_answer(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _user_task_done(gs: dict, username: str, task_id: str) -> bool:
    return task_id in gs.get("task_done_by_user", {}).get(username, {})


def _mark_user_task_done(gs: dict, username: str, task_id: str):
    gs.setdefault("task_done_by_user", {}).setdefault(username, {})[task_id] = datetime.utcnow().isoformat()


def _team_task_done(gs: dict, team: str, task_id: str) -> bool:
    """Check if a team has completed a bot/sovereign task."""
    return task_id in gs.get("task_done_by_team", {}).get(team, {})


def _mark_team_task_done(gs: dict, team: str, task_id: str):
    """Mark a bot/sovereign task as completed by a team."""
    gs.setdefault("task_done_by_team", {}).setdefault(team, {})[task_id] = datetime.utcnow().isoformat()


def _visible_ap(gs: dict, team: str) -> int:
    """UI-only AP that can include hidden shadow points until epoch rollover."""
    real_ap = int(gs["ap"].get(team, 0))
    shadow_ap = int(gs.get("shadow_task_ap", {}).get(team, 0))
    return real_ap + shadow_ap


def _active_backstabber_for_team(gs: dict, target_team: str) -> str | None:
    """Return the queued backstabber for target_team in the current epoch, if any."""
    queued = gs.get("queued_actions", {})
    for actor, action in queued.items():
        if action.get("action") != "BACKSTAB":
            continue
        if action.get("target") != target_team:
            continue
        if int(gs["hp"].get(actor, 0)) <= 0:
            continue
        return actor
    return None


def _apply_task_rewards(gs: dict, solver_team: str, pts: int, task_title: str, solver_label: str):
    """
    Apply task rewards with alliance and betrayal rules:
    - Normal: solver team gets +pts; all active allies get +pts.
    - If solver team is actively targeted by a queued backstab this epoch:
      solver team gets 0 real AP, backstabber gets +2*pts, solver team gets
      shadow AP for UI until epoch rollover.
    """
    betrayer = _active_backstabber_for_team(gs, solver_team)
    if betrayer:
        gs["ap"][betrayer] = int(gs["ap"].get(betrayer, 0)) + (pts * 2)
        gs.setdefault("shadow_task_ap", {})[solver_team] = int(gs.get("shadow_task_ap", {}).get(solver_team, 0)) + pts
        push_ev("TASK", f"{solver_label} completed '{task_title}' +{pts} AP", solver_team)
        return

    gs["ap"][solver_team] = int(gs["ap"].get(solver_team, 0)) + pts

    # Alliance sharing: allies receive full, non-halved points.
    for ally in gs.get("alliances", {}).get(solver_team, []):
        if int(gs["hp"].get(ally, 0)) <= 0:
            continue
        gs["ap"][ally] = int(gs["ap"].get(ally, 0)) + pts

    push_ev("TASK", f"{solver_label} completed '{task_title}' +{pts} AP", solver_team)


def _task_attempt_panel(task: dict, team: str, username: str):
    task_id = task["id"]
    portal = MONARCH_TASK_PORTAL.get(task_id, {})
    drive_url = portal.get("drive_url", "")
    expected_answer = portal.get("answer", "")

    st.markdown(f"### {task['title']}")
    st.markdown(task["desc"])

    if drive_url:
        st.markdown(f"[📎 Download File]({drive_url})")

    live_gs = load_gs()

    if _user_task_done(live_gs, username, task_id):
        st.success("You already solved this task.")
        return

    answer = st.text_input("Your Answer", key=f"ans_{task_id}", placeholder="Type your answer")
    c1, c2 = st.columns(2)
    with c1:
        submit_clicked = st.button("Submit", use_container_width=True, key=f"submit_{task_id}")
    with c2:
        cancel_clicked = st.button("Cancel", use_container_width=True, key=f"cancel_{task_id}")

    if cancel_clicked:
        st.rerun()

    if submit_clicked:
        current_gs = load_gs()

        if _user_task_done(current_gs, username, task_id):
            st.info("Already solved earlier.")
            st.rerun()



        if not expected_answer:
            st.error("Answer key is not configured for this task.")
            return

        if _normalize_answer(answer) == _normalize_answer(expected_answer):
            _apply_task_rewards(
                current_gs,
                solver_team=team,
                pts=int(task["pts"]),
                task_title=task["title"],
                solver_label=username,
            )
            _mark_user_task_done(current_gs, username, task_id)
            save_gs(current_gs)
            st.success("Correct answer. AP awarded.")
            st.rerun()
        else:
            st.error("Wrong answer.")
            push_ev("TASK", f"Wrong answer on {task_id} by {username}.", team)
            st.rerun()


def _mount_live_timer_sync(epoch_end_iso: str, epoch_duration_secs: int):
    """Update only header timer/progress in the browser every second (no full rerun)."""
    end_iso_js = (epoch_end_iso or "").strip()

    components.html(
        f"""
        <script>
            const END_ISO = {json.dumps(end_iso_js)};
            const EPOCH_SECS = {epoch_duration_secs};
            let END_MS = Date.parse(END_ISO.endsWith('Z') ? END_ISO : (END_ISO + 'Z'));
            if (Number.isNaN(END_MS)) {{
                END_MS = Date.now() + (EPOCH_SECS * 1000);
            }}

            const parentWin = window.parent;
            const doc = parentWin.document;

            function tick() {{
                const timerEl = doc.getElementById('ot-live-timer');
                const barEl = doc.getElementById('ot-live-bar');
                if (!timerEl || !barEl) return;

                const rem = Math.max(0, Math.floor((END_MS - Date.now()) / 1000));
                const mm = String(Math.floor(rem / 60)).padStart(2, '0');
                const ss = String(rem % 60).padStart(2, '0');
                timerEl.textContent = `${{mm}}:${{ss}}`;
                timerEl.style.opacity = '1';

                const pct = Math.max(0, Math.min(100, (rem / EPOCH_SECS) * 100));
                barEl.style.width = `${{pct.toFixed(1)}}%`;

                timerEl.style.color = rem <= 60 ? '#FF2244' : '#FFD700';
            }}

            if (parentWin.__otClockInterval) {{
                clearInterval(parentWin.__otClockInterval);
            }}
            tick();
            parentWin.__otClockInterval = setInterval(tick, 1000);
        </script>
        """,
        height=0,
    )


def show_war_room():
    username = st.session_state.username
    user     = get_user(username)
    MT       = user["team"]
    dn       = user.get("display_name", username)

    # ── SESSION DEFAULTS ─────────────────────────────────────
    # Check URL query params to restore tab across browser refresh
    tab_from_url = st.query_params.get("tab", "Home")
    valid_tabs = ["Home", "Tasks (Human)", "Tasks (Bot)", "Strategy Deck", "Leaderboard"]
    if tab_from_url not in valid_tabs:
        tab_from_url = "Home"
    
    if "active_tab" not in st.session_state: 
        st.session_state.active_tab = tab_from_url
    
    if "ws_log"     not in st.session_state: st.session_state.ws_log     = []
    if "code_outputs" not in st.session_state: st.session_state.code_outputs = {}
    if "bot_code"   not in st.session_state: 
        st.session_state.bot_code = "# Auto-Generated Standard Tactics\\n# Output format: ATTACK, <cell_index>\\nprint('DEFEND')"

    # ── LOAD DATA ────────────────────────────────────────────
    gs    = _cached_load_gs()
    evs   = _cached_load_evs(40)
    teams = _cached_load_teams()
    tc    = terr_count(gs["grid"], list(teams.keys()))

    try:
        epoch_end = datetime.fromisoformat(gs["epoch_end"])
        remaining = max(0.0, (epoch_end - datetime.utcnow()).total_seconds())
    except Exception:
        remaining = EPOCH_DURATION_SECS

    # ── EPOCH STATE TRACKING (Rerun only when epoch changes) ──
    if "last_epoch_seen" not in st.session_state:
        st.session_state.last_epoch_seen = gs.get("epoch", 0)
    
    # Detect epoch change and trigger check
    current_epoch = gs.get("epoch", 0)
    if current_epoch > st.session_state.last_epoch_seen:
        st.session_state.last_epoch_seen = current_epoch

    # Smart background check: frequent near epoch end, sparse otherwise
    # Prevents 5-8s delay when timer hits 0
    check_interval = 5000 if remaining <= 10 else 30000
    st_autorefresh(interval=check_interval, limit=None, key="ot_epoch_check")

    if "queued_attacks" not in gs: gs["queued_attacks"] = []
    if "shadow_task_ap" not in gs: gs["shadow_task_ap"] = {}
    
    # Check if epoch rolled over
    if remaining <= 0 and not gs.get("game_over"):
        # Trigger epoch switch
        gs["epoch"] += 1
        gs["epoch_end"] = (datetime.utcnow() + timedelta(seconds=EPOCH_DURATION_SECS)).isoformat()
        queued = gs.get("queued_actions", {})
        gs["queued_actions"] = {}
        queued_attacks = gs.get("queued_attacks", [])
        gs["queued_attacks"] = []
        blocked_backstabbers = set()
        
        # 1. Resolve Suspicions
        for actor, action in list(queued.items()):
            if action["action"] == "SUSPICION":
                target = action["target"]
                target_action = queued.get(target)
                if target_action and target_action["action"] == "BACKSTAB" and target_action["target"] == actor:
                    # caught! target damaged
                    damage = 3000
                    gs["hp"][target] = max(0, int(gs["hp"].get(target, 0)) - damage)
                    blocked_backstabbers.add(target)
                    push_ev("SYS", f"JUDICIAL DISCOVERY: {actor} caught {target} preparing a backstab! {target} suffers -{damage} HP.", actor)
                else:
                    # false accusation! actor damaged
                    damage = 3000
                    gs["hp"][actor] = max(0, int(gs["hp"].get(actor, 0)) - damage)
                    push_ev("SYS", f"JUDICIAL FAILURE: {actor} falsely accused {target}. {actor} suffers -{damage} HP.", actor)
                
        # 2. Resolve Backstabs
        for actor, action in list(queued.items()):
            if action["action"] == "BACKSTAB" and gs["hp"].get(actor, 0) > 0 and actor not in blocked_backstabbers:
                target = action["target"]
                # Break alliance
                if actor in gs["alliances"] and target in gs["alliances"][actor]: gs["alliances"][actor].remove(target)
                if target in gs["alliances"] and actor in gs["alliances"][target]: gs["alliances"][target].remove(actor)
                
                # massively damage target
                damage = 3000
                if target in gs["hp"]:
                    gs["hp"][target] = max(0, int(gs["hp"][target]) - damage)
                    push_ev("ATTACK", f"BETRAYAL! {actor} backstabbed {target} for {damage} HP damage!", actor)
        
        # 3. Resolve queued human attacks in submission order.
        for attack in queued_attacks:
            actor = attack.get("actor")
            target = attack.get("target")
            requested_hits = int(attack.get("hits", 1) or 1)

            if not actor or not target or actor == target:
                continue
            if int(gs["hp"].get(actor, 0)) <= 0:
                push_ev("SYS", f"Queued attack skipped: {actor} is eliminated.", actor)
                continue
            if int(gs["hp"].get(target, 0)) <= 0:
                push_ev("SYS", f"Queued attack skipped: target {target} is already eliminated.", actor)
                continue

            ap_available = int(gs["ap"].get(actor, 0))
            max_hits = ap_available // ATTACK_COST_AP
            executed_hits = min(requested_hits, max_hits)
            if executed_hits <= 0:
                push_ev("SYS", f"Queued attack failed: {actor} has insufficient AP.", actor)
                continue

            damage = executed_hits * 100
            gs["ap"][actor] = ap_available - (executed_hits * ATTACK_COST_AP)
            gs["hp"][target] = max(0, int(gs["hp"].get(target, 0)) - damage)
            
            # Territory loss on heavy damage (>1500 dmg = lose 1-3 cells to wilderness)
            if damage > 1500:
                cells_to_lose = min(3, damage // 1000)
                target_cells = [i for i, cell in enumerate(gs["grid"]) if cell == target]
                if target_cells and cells_to_lose > 0:
                    import random
                    for _ in range(min(cells_to_lose, len(target_cells))):
                        cell_idx = random.choice(target_cells)
                        gs["grid"][cell_idx] = ""
                        target_cells.remove(cell_idx)
            
            # Territory steal on multi-hit attacks (3+ hits = steal 1 territory from target)
            if executed_hits >= 3:
                target_cells = [i for i, cell in enumerate(gs["grid"]) if cell == target]
                if target_cells:
                    import random
                    stolen_cell = random.choice(target_cells)
                    gs["grid"][stolen_cell] = actor
                    push_ev(
                        "ATTACK",
                        f"TERRITORIAL CONQUEST: {actor} stole cell #{stolen_cell} from {target}!",
                        actor,
                    )
            
            push_ev(
                "ATTACK",
                f"EPOCH STRIKE: {actor} executed {executed_hits}/{requested_hits} hits on {target} (-{damage} HP, -{executed_hits * ATTACK_COST_AP} AP).",
                actor,
            )

        # 4. Clean up eliminated map territories
        for t, hp in list(gs["hp"].items()):
            if hp <= 0:
                for i in range(len(gs["grid"])):
                    if gs["grid"][i] == t:
                        gs["grid"][i] = ""
        
        # 5. Territory-Based AP Generation (Economy)
        for team in list(gs["hp"].keys()):
            if gs["hp"].get(team, 0) > 0:
                terr = sum(1 for cell in gs["grid"] if cell == team)
                ap_gain = terr * 50
                gs["ap"][team] = int(gs["ap"].get(team, 0)) + ap_gain
                if ap_gain > 0:
                    push_ev("SYS", f"{team} earned +{ap_gain} AP from {terr} territories.", team)
                        
        # 6. Victory Assessment
        living = [t for t, hp in gs["hp"].items() if hp > 0]
        if gs["epoch"] > 1 and len(gs["hp"]) > 1:
            if len(living) == 1:
                gs["game_over"] = living[0]
            elif len(living) == 0:
                gs["game_over"] = "DRAW"

        # Shadow AP masking only applies within an epoch.
        gs["shadow_task_ap"] = {}

        save_gs(gs)
        st.rerun()

    pct_left  = remaining / EPOCH_DURATION_SECS
    mins_left = int(remaining // 60)
    secs_left = int(remaining % 60)
    MY_COLOR  = teams.get(MT, {}).get("color", "#0099FF")
    MY_ICON   = teams.get(MT, {}).get("icon", "🔵")

    # ── STYLES ───────────────────────────────────────────────
    st.markdown(get_full_css(), unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            transform: translateX(0%) !important;
            min-width: 320px !important;
            max-width: 320px !important;
        }
        [data-testid="collapsedControl"] { display: block !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    components.html(
        """
        <script>
            const doc = window.parent.document;
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            const toggleBtn = doc.querySelector('[data-testid="collapsedControl"] button');
            if (sidebar && sidebar.getAttribute('aria-expanded') === 'false' && toggleBtn) {
                toggleBtn.click();
            }
        </script>
        """,
        height=0,
    )


    # ── SIDEBAR ───────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class="sb-head">
            <div class="ot-logo" style="font-size:1.1rem;letter-spacing:4px">OVERTHRONE</div>
            <div class="ot-subtitle" style="margin-top:3px">HELIX x ISTE · WAR ROOM OS v5.0</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-title">SOVEREIGN IDENTITY</div>
            <div class="sb-row"><span class="sb-lbl">USER</span><span class="sb-val" style="color:{MY_COLOR}">{dn}</span></div>
            <div class="sb-row"><span class="sb-lbl">TEAM</span><span class="sb-val" style="color:{MY_COLOR}">{MY_ICON} {MT}</span></div>
        </div>
        """, unsafe_allow_html=True)

        my_meta = teams.get(MT, {})
        members = my_meta.get("members", [username])
        all_users = _cached_load_users()
        member_names = [all_users.get(m, {}).get("display_name", m) for m in members]
        pills = "".join(f'<span class="member-pill">{n}</span>' for n in member_names)
        st.markdown(f'<div class="sb-section"><div class="sb-title">TEAM ROSTER</div>{pills}</div>', unsafe_allow_html=True)

        my_hp   = int(gs["hp"].get(MT, STARTING_HP))
        my_ap   = _visible_ap(gs, MT)
        my_terr = tc.get(MT, 0)
        hp_p = max(0, my_hp / STARTING_HP)
        ap_p = min(my_ap / float(STARTING_AP*2), 1.0)

        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-title">BIOMETRICS · LIVE</div>
            <div class="sb-row"><span class="sb-lbl">HEALTH POINTS</span><span class="sb-val" style="color:{MY_COLOR}">{my_hp:,}</span></div>
            <div class="mini-bar" style="margin-bottom:8px">
                <div class="mini-bar-f" style="width:{hp_p*100:.0f}%;background:{MY_COLOR};box-shadow:0 0 5px {MY_COLOR}"></div>
            </div>
            <div class="sb-row"><span class="sb-lbl">ATTACK POINTS</span><span class="sb-val" style="color:#00E5FF">{my_ap:,}</span></div>
            <div class="mini-bar" style="margin-bottom:8px">
                <div class="mini-bar-f" style="width:{ap_p*100:.0f}%;background:#00E5FF;box-shadow:0 0 5px #00E5FF"></div>
            </div>
            <div class="sb-row"><span class="sb-lbl">TERRITORY</span><span class="sb-val" style="color:#D4AF37">{my_terr} / 30 cells</span></div>
            <div class="mini-bar"><div class="mini-bar-f" style="width:{my_terr}%;background:#D4AF37"></div></div>
        </div>
        """, unsafe_allow_html=True)

        timer_color = "#FF2244" if remaining <= 60 else "#FFD700"
        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-title">EPOCH STATUS</div>
            <div class="sb-row"><span class="sb-lbl">EPOCH</span><span class="sb-val" style="color:#D4AF37">{gs['epoch']}</span></div>
            <div class="sb-row"><span class="sb-lbl">REMAINING</span><span class="sb-val" style="color:{timer_color};font-weight:700">{mins_left:02d}:{secs_left:02d}</span></div>
            <div class="mini-bar" style="margin-top:6px">
                <div class="mini-bar-f" style="width:{pct_left*100:.0f}%;background:linear-gradient(90deg,#D4AF37,#FFD700)"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sb-section"><div class="sb-title">NETWORK</div>', unsafe_allow_html=True)
        if st.button("LOGOUT / RECONNECT", use_container_width=True):
            for k in ["logged_in","username","user_data","active_tab","bot_code"]:
                st.session_state.pop(k, None)
            for k in ["user", "tab", "admin"]:
                st.query_params.pop(k, None)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── HEADER ───────────────────────────────────────────────
    st.markdown(f"""
<div class="ot-hdr">
    <div>
        <div class="ot-logo">OVERTHRONE</div>
        <div class="ot-subtitle">HELIX x ISTE · THE ULTIMATE KINGDOM SIMULATION</div>
    </div>
    <div style="display:flex;align-items:center;gap:1.2rem">
        <span class="ot-live-badge">LIVE</span>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.58rem;color:{MY_COLOR}">
            {MY_ICON} {dn.upper()} · {MT}
        </div>
    </div>
    <div class="ot-epoch-box">
        <div class="ot-epoch-num">EPOCH {gs['epoch']}</div>
        <div class="ot-epoch-phase">{gs['phase']}</div>
    </div>
        <div class="ot-timer" id="ot-live-timer" style="color:{timer_color};opacity:0">--:--</div>
</div>
<div class="ot-tbar"><div class="ot-tbar-fill" id="ot-live-bar" style="width:{pct_left*100:.1f}%"></div></div>
""", unsafe_allow_html=True)
    _mount_live_timer_sync(gs["epoch_end"], EPOCH_DURATION_SECS)

    # ── VICTORY CONDITION DISPLAY ────────────────────────────
    if gs.get("game_over"):
        winner = gs["game_over"]
        title = "SOVEREIGNTY ACHIEVED" if winner != "DRAW" else "MUTUAL DESTRUCTION"
        desc = f"Kingdom {winner} is the sole survivor." if winner != "DRAW" else "No kingdoms survived the final epoch. The realm falls to ruin."
        st.markdown(f"""
        <div style="background:var(--void); border-top:1px solid var(--gold); border-bottom:1px solid var(--gold); padding:80px 20px; text-align:center; box-shadow:0 0 100px rgba(212,175,55,0.2) inset; animation:pulse 3s infinite;">
            <h1 style="font-family:'Orbitron',monospace; color:var(--goldb); margin:0; font-size:4rem; text-shadow:0 0 30px var(--gold); letter-spacing:10px">{title}</h1>
            <p style="font-family:'Share Tech Mono',monospace; color:var(--text); margin-top:20px; font-size:1.5rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
        return  # Halt loading normal dashboard
        
    # ── MAIN TABS ────────────────────────────────────────────
    tab_names = ["Home", "Tasks (Human)", "Tasks (Bot)", "Strategy Deck", "Leaderboard"]
    tab_cols  = st.columns(len(tab_names), gap="small")
    for i, tname in enumerate(tab_names):
        with tab_cols[i]:
            btn_cls = "nav-tab-btn active" if st.session_state.active_tab == tname else "nav-tab-btn"
            st.markdown(f'<div class="{btn_cls}"></div>', unsafe_allow_html=True) # Styling hack
            if st.button(tname, key=f"tab_{tname}", use_container_width=True):
                st.session_state.active_tab = tname
                st.query_params["tab"] = tname
                st.rerun()

    active = st.session_state.active_tab
    st.markdown(f"<div style='font-family:ShareTechMono,monospace;font-size:0.55rem;color:var(--dim);margin:12px 0'>► {active.upper()}</div>", unsafe_allow_html=True)

    is_eliminated = gs["hp"].get(MT, 0) <= 0

    if is_eliminated and active not in ["Home", "Leaderboard"]:
        st.markdown(f"""
        <div style="background:rgba(255,10,50,0.1); border:1px solid #FF2244; padding:60px 20px; text-align:center; border-radius:10px; box-shadow:0 0 80px rgba(255,10,50,0.3) inset;">
            <h1 style="font-family:'Orbitron',monospace; color:#FF2244; margin:0; font-size:3rem; text-shadow:0 0 20px #FF2244; letter-spacing:10px">KINGDOM FALLEN</h1>
            <p style="font-family:'Share Tech Mono',monospace; color:#ccc; margin-top:20px; font-size:1.2rem;">Your HP has reached 0. You are permanently eliminated from the war. Watch the Leaderboard or return Home.</p>
        </div>
        """, unsafe_allow_html=True)
    # ─────────────────────────────────────────────────────────────
    # HOME TAB (Grid Map + Comms Feed)
    # ─────────────────────────────────────────────────────────────
    elif active == "Home":
        left_col, right_col = st.columns([2.3, 1], gap="large")

        with left_col:
            total_claimed = sum(1 for c in gs["grid"] if c)
            unclaimed = 30 - total_claimed
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <div style="font-family:'Orbitron',monospace;font-size:0.5rem;letter-spacing:4px;color:#64ff96;text-shadow:0 0 8px #00ff5566">
                    🗺️ BATTLE ZONE · ORGANIC NEON
                </div>
                <div style="display:flex;gap:14px">
                    <span style="font-family:'Orbitron',monospace;font-size:0.52rem;color:#fff">
                        ☠️ {total_claimed} CLAIMED &nbsp;|&nbsp; 🟢 {unclaimed} FREE
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            team_colors_json = json.dumps({k: v.get("bg", "#0a1a0e") for k,v in teams.items()})
            team_strokes_json = json.dumps({k: v.get("color", "#0a150c") for k,v in teams.items()})
            grid_json = json.dumps(gs["grid"])

            team_meta_dict = {}
            for t_id, t_dict in teams.items():
                mems = len(t_dict.get("members", []))
                team_meta_dict[t_id] = {
                    "hp": gs["hp"].get(t_id, 0),
                    "ap": _visible_ap(gs, t_id),
                    "terr": sum(1 for x in gs["grid"] if x == t_id),
                    "members": mems
                }
            metadata_json = json.dumps(team_meta_dict)

            d3_map_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/d3-delaunay@6"></script>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Share+Tech+Mono&display=swap');
                body {{ margin: 0; padding: 0; background-color: transparent; }}
                .voronoi-cell {{ stroke-width: 1.5px; transition: fill 0.3s, opacity 0.3s; cursor: crosshair; }}
                .voronoi-cell:hover {{ opacity: 0.8; stroke: #fff !important; stroke-width: 2.5px !important; z-index: 10; }}
                .amoeba-border {{ stroke: rgba(100,255,100,0.3); stroke-width: 2; fill: none; stroke-dasharray: 5,5; filter: drop-shadow(0 0 8px rgba(0,255,100,0.4)); }}
                .map-wrap {{
                    background:linear-gradient(135deg,#020d08 0%,#030f0a 40%,#020a06 100%);
                    border:1px solid rgba(100,255,100,0.15); border-radius:6px;
                    box-shadow:inset 0 0 80px rgba(0,0,0,0.6);
                    position:relative;overflow:hidden;
                    width: 100%; height: 500px;
                }}
                #d3-tooltip {{
                    position: absolute; background: rgba(5, 10, 15, 0.95); border: 1px solid #D4AF37; border-radius: 4px;
                    padding: 10px; color: #fff; font-family: 'Share Tech Mono', monospace; font-size: 12px;
                    pointer-events: none; opacity: 0; transition: opacity 0.1s; z-index: 100; box-shadow: 0 0 15px rgba(0,0,0,0.8);
                }}
                .tt-title {{ font-family: 'Orbitron', monospace; color: #D4AF37; font-size:14px; margin-bottom:5px; border-bottom:1px solid rgba(212,175,55,0.3); padding-bottom:3px;}}
                .tt-row {{ display:flex; justify-content:space-between; width:140px; margin-bottom:2px;}}
                .tt-lbl {{ color: #888; }}
                .tt-val {{ color: #00E5FF; font-weight:700; }}
            </style>
            </head>
            <body>
            <div class="map-wrap">
            <div id="d3-map" style="width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;"></div>
            <div id="d3-tooltip"></div>
            </div>
            <script>
                const width = 600, height = 500;
                const svg = d3.select("#d3-map").append("svg")
                    .attr("viewBox", `0 0 ${{width}} ${{height}}`)
                    .attr("style", "width:100%; height:100%; display:block; padding: 10px;");
                
                const n = 30;
                const points = [];
                const phi = (1 + Math.sqrt(5)) / 2;
                for(let i=0; i<n; i++) {{
                    let r = 180 * Math.sqrt((i+0.5)/n);
                    let theta = 2 * Math.PI * i / phi;
                    let noiseX = (Math.sin(i*123) * 15);
                    let noiseY = (Math.cos(i*321) * 15);
                    points.push([width/2 + r * Math.cos(theta) + noiseX, height/2 + r * Math.sin(theta) + noiseY]);
                }}
                
                const delaunay = d3.Delaunay.from(points);
                const voronoi = delaunay.voronoi([0, 0, width, height]);
                const pData = points.map((p, i) => ({{p: p, i: i}}));
                
                const data = {grid_json};
                const backgrounds = {team_colors_json};
                const strokes = {team_strokes_json};
                const meta = {metadata_json};
                const tooltip = d3.select("#d3-tooltip");
                
                const g = svg.append("g");
                
                g.append("g")
                   .selectAll("path")
                   .data(pData)
                   .join("path")
                   .attr("class", "voronoi-cell")
                   .attr("d", d => voronoi.renderCell(d.i))
                   .attr("fill", d => {{
                       let owner = data[d.i];
                       if(owner && backgrounds[owner]) return backgrounds[owner];
                       return (d.i%3===0) ? "#0a1f0a" : "#0d1a0d";
                   }})
                   .attr("stroke", d => {{
                       let owner = data[d.i];
                       if(owner && strokes[owner]) return strokes[owner];
                       return "#081a08";
                   }})
                   .attr("style", d => {{
                       let owner = data[d.i];
                       if(owner && meta[owner]) {{
                           let hp = meta[owner].hp;
                           let glow = Math.min(25, Math.max(0, (hp - 1000) / 400));
                           let col = strokes[owner] || "#ffffff";
                           return `filter: drop-shadow(0px 0px ${{glow}}px ${{col}});`;
                       }}
                       return "";
                   }})
                   .on("mouseover", (e, d) => {{
                       let owner = data[d.i];
                       let content = `<div class="tt-title">CELL ${{d.i}} · ${{(owner || "WILDERNESS").toUpperCase()}}</div>`;
                       if(owner && meta[owner]) {{
                           let m = meta[owner];
                           content += `<div class="tt-row"><span class="tt-lbl">HP</span><span class="tt-val" style="color:#FF2244">${{m.hp.toLocaleString()}}</span></div>`;
                           content += `<div class="tt-row"><span class="tt-lbl">AP</span><span class="tt-val">${{m.ap.toLocaleString()}}</span></div>`;
                           content += `<div class="tt-row"><span class="tt-lbl">AREA</span><span class="tt-val" style="color:#D4AF37">${{m.terr}}</span></div>`;
                           content += `<div class="tt-row"><span class="tt-lbl">MEMBERS</span><span class="tt-val" style="color:#00CC88">${{m.members}}</span></div>`;
                       }} else {{
                           content += `<div style="text-align:center;color:#888;margin-top:8px;font-style:italic">UNASSIGNED WILDERNESS</div>`;
                       }}
                       tooltip.html(content).style("opacity", 1);
                   }})
                   .on("mousemove", (e) => {{
                       let rect = document.querySelector('.map-wrap').getBoundingClientRect();
                       let mx = e.clientX - rect.left;
                       let my = e.clientY - rect.top;
                       tooltip.style("left", (mx + 15) + "px").style("top", (my - 20) + "px");
                   }})
                   .on("mouseout", () => {{
                       tooltip.style("opacity", 0);
                   }});
                   
                const expandedHull = d3.polygonHull(points.map(p => [p[0] + (p[0]-width/2)*0.16, p[1] + (p[1]-height/2)*0.16]));
                g.append("path")
                   .attr("class", "amoeba-border")
                   .attr("d", "M" + expandedHull.join("L") + "Z");

                // Render cell ids for visibility 
                g.append("g")
                   .selectAll("text")
                   .data(pData)
                   .join("text")
                   .attr("x", d => d.p[0])
                   .attr("y", d => d.p[1])
                   .attr("dy", "0.3em")
                   .attr("text-anchor", "middle")
                   .attr("fill", "rgba(255,255,255,0.85)")
                   .attr("style", "font-family:'Share Tech Mono'; font-size:11px; font-weight:700; pointer-events:none; filter: drop-shadow(0px 1px 3px rgba(0,0,0,1));")
                   .text(d => d.i);
                   
                // Zoom & Pan functionality
                const zoom = d3.zoom()
                    .scaleExtent([0.5, 4])
                    .on("zoom", (e) => {{
                        g.attr("transform", e.transform);
                    }});
                svg.call(zoom);
            </script>
            </body>
            </html>
            """
            
            components.html(d3_map_html, height=520, scrolling=False)

            legend_html = ""
            for tname, tinfo in teams.items():
                terr_pct = tc.get(tname, 0)
                legend_html += f'<div class="legend-item"><div class="legend-dot" style="background:{tinfo.get("color","#555")};box-shadow:0 0 6px {tinfo.get("color","#555")}"></div>{tinfo.get("icon","·")} {tname} <span style="color:{tinfo.get("color","#555")};margin-left:3px">{terr_pct}</span></div>'
            legend_html += f'<div class="legend-item"><div class="legend-dot" style="background:#0a1a0e;border:1px solid #1a3a1a"></div>FREE ZONE ({unclaimed})</div>'

            st.markdown(f"""
            <div class="map-legend">{legend_html}</div>
            """, unsafe_allow_html=True)

        with right_col:
            st.markdown('<div class="sec-lbl">COMMS FEED · LIVE</div>', unsafe_allow_html=True)
            feed_html = '<div class="ev-feed">'
            for ev in evs[:22]:
                bc = EVENT_COLORS.get(ev.get("kind","SYS"), "#333355")
                feed_html += f'<div class="ev-item" style="border-left-color:{bc}"><span class="ev-ts">{ev.get("ts","--:--:--")}</span><span class="ev-msg">{ev.get("msg","")}</span></div>'
            feed_html += '</div>'
            st.markdown(feed_html, unsafe_allow_html=True)
            
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="sec-lbl">ELIMINATION TRACKER</div>', unsafe_allow_html=True)
            ranked_e = sorted(teams.items(), key=lambda x: int(gs["hp"].get(x[0], 0)), reverse=True)
            for tname, tinfo in ranked_e:
                hp = int(gs["hp"].get(tname, STARTING_HP))
                status = "ELIMINATED" if hp <= 0 else "ACTIVE"
                sc = "#FF2244" if hp <= 0 else "#00CC88"
                st.markdown(f"""
                <div class="elim-row">
                    <span style="color:{tinfo.get('color','#fff')}">{tinfo.get('icon','·')} TEAM {tname}</span>
                    <span style="font-family:'Orbitron',monospace;font-size:0.48rem;letter-spacing:2px;color:{sc}">{status}</span>
                </div>
                """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────
    # TASKS HUMAN
    # ─────────────────────────────────────────────────────────────
    elif active == "Tasks (Human)":
        st.markdown('<div class="sec-lbl">🧠 HUMAN TASKS · ATTEMPT & SUBMIT</div>', unsafe_allow_html=True)
        tc_cols = st.columns(2, gap="small")
        for i, task in enumerate(TASKS["monarch"]):
            dc = DIFF_COLOR[task["diff"]]
            solved = _user_task_done(gs, username, task["id"])
            with tc_cols[i % 2]:
                solved_badge = '<div style="color:#00CC88;font-size:0.72rem;margin-top:6px">✅ Solved</div>' if solved else ""
                link_indicator = '🔗' if task.get("link") else ""
                st.markdown(f"""
                <div class="tc" style="border-top:2px solid {dc}44">
                    <div class="tc-diff" style="background:{dc}18;color:{dc};border:1px solid {dc}44">{task['diff']}</div>
                    <div class="tc-title">{task['title']} {link_indicator}</div>
                    <div class="tc-desc">{task['desc']}</div>
                    <div class="tc-pts">+{task['pts']} AP</div>
                    {solved_badge}
                </div>
                """, unsafe_allow_html=True)
                btn_cols = st.columns([1, 1] if task.get("link") else [1], gap="small")
                btn_label = "DONE" if solved else f"ATTEMPT +{task['pts']} AP"
                
                with btn_cols[0]:
                    if solved:
                        st.button(btn_label, key=f"attempt_{task['id']}", use_container_width=True, disabled=True)
                    else:
                        with st.popover(btn_label, key=f"attempt_popover_{task['id']}", use_container_width=True):
                            _task_attempt_panel(task, MT, username)
                
                if task.get("link") and len(btn_cols) > 1:
                    with btn_cols[1]:
                        st.link_button("📎 File", task["link"], use_container_width=True)

    # ─────────────────────────────────────────────────────────────
    # TASKS BOT (Code editor)
    # ─────────────────────────────────────────────────────────────
    elif active == "Tasks (Bot)":
        from config import BOT_TASKS
        from db import run_bot_task
        
        st.markdown('<div class="sec-lbl">💻 BOT TASKS · PYTHON CHALLENGES</div>', unsafe_allow_html=True)
        
        # Organize tasks by category (using per-team tracking)
        team_bot_tasks = gs.get("task_done_by_team", {}).get(MT, {})
        categories = {}
        for task_id, task in BOT_TASKS.items():
            cat = task["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(task)
        
        # Count solved per category
        cat_progress = {}
        cat_list = ["Neural Architect", "Cipher Breaker", "Stream Vector", "Strategy Matrix", "Anomaly Guard", "Resource Optimizer"]
        for cat in cat_list:
            if cat in categories:
                solved_count = sum(1 for t in categories[cat] if t["id"] in team_bot_tasks)
                cat_progress[cat] = (solved_count, len(categories[cat]))
        
        # Category selector (tabs)
        tab_cols = st.columns(len(cat_list), gap="small")
        selected_cat = None
        for idx, cat in enumerate(cat_list):
            if cat not in categories:
                continue
            solved_cnt, total_cnt = cat_progress.get(cat, (0, 0))
            with tab_cols[idx]:
                if st.button(f"{cat[:12]}\n{solved_cnt}/{total_cnt}", use_container_width=True, key=f"cat_btn_{cat}"):
                    st.session_state["selected_bot_cat"] = cat
        
        # Get selected category (persist in session)
        selected_cat = st.session_state.get("selected_bot_cat", cat_list[0])
        if selected_cat not in categories:
            selected_cat = cat_list[0]
            st.session_state["selected_bot_cat"] = selected_cat
        
        # Show task cards in 2-column layout
        if selected_cat in categories:
            tasks_in_cat = sorted(categories[selected_cat], key=lambda t: t["id"])
            task_cols = st.columns(2, gap="small")
            
            for idx, task in enumerate(tasks_in_cat):
                task_id = task["id"]
                is_solved = task_id in team_bot_tasks
                dc = DIFF_COLOR[task["difficulty"]]
                
                with task_cols[idx % 2]:
                    solved_badge = '<div style="color:#00CC88;font-size:0.72rem;margin-top:6px">✅ Solved</div>' if is_solved else ""
                    st.markdown(f"""
                    <div class="tc" style="border-top:2px solid {dc}44">
                        <div class="tc-diff" style="background:{dc}18;color:{dc};border:1px solid {dc}44">{task['difficulty']}</div>
                        <div class="tc-title">{task['id']} · {task['title']}</div>
                        <div class="tc-desc">{task['description']}</div>
                        <div class="tc-pts">+{task['ap_reward']} AP</div>
                        {solved_badge}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    btn_label = "SOLVE" if not is_solved else "DONE"
                    if st.button(btn_label, key=f"open_bot_{task_id}", use_container_width=True, disabled=is_solved):
                        st.session_state["selected_bot_task"] = task_id
                        st.rerun()
        
        # Task detail view (modal-like experience)
        if "selected_bot_task" in st.session_state:
            task_id = st.session_state["selected_bot_task"]
            if task_id in BOT_TASKS:
                task = BOT_TASKS[task_id]
                
                st.divider()
                
                # Header
                st.markdown(f'<div style="font-family:Orbitron,monospace;font-size:1.3rem;color:var(--gold);margin-bottom:8px">{task["id"]} · {task["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:0.9rem;color:var(--dim);margin-bottom:16px">{task["description"]}</div>', unsafe_allow_html=True)
                
                # Code editor
                code_key = f"bot_code_{task_id}"
                if code_key not in st.session_state:
                    st.session_state[code_key] = task["template"]
                
                st.markdown("**Your Code**")
                user_code = st.text_area(
                    "Enter your solution",
                    value=st.session_state[code_key],
                    height=280,
                    key=f"bot_editor_{task_id}",
                    label_visibility="collapsed"
                )
                st.session_state[code_key] = user_code
                
                # Buttons
                col1, col2, col3 = st.columns([2, 1, 1], gap="small")
                with col1:
                    submit_btn = st.button(
                        f"🚀 SUBMIT (+{task['ap_reward']} AP)",
                        key=f"submit_{task_id}",
                        use_container_width=True,
                        type="primary"
                    )
                with col2:
                    if st.button("Reset", key=f"reset_{task_id}", use_container_width=True):
                        st.session_state[code_key] = task["template"]
                        st.rerun()
                with col3:
                    if st.button("Back", key=f"back_{task_id}", use_container_width=True):
                        st.session_state["selected_bot_task"] = None
                        st.rerun()
                
                # Submission handling
                if submit_btn:
                    with st.spinner("Verifying..."):
                        success, token_or_msg = run_bot_task(task_id, user_code, MT, gs)
                        
                        if success:
                            # Verification passed - now apply rewards with backstab/suspicion mechanics
                            _apply_task_rewards(
                                gs,
                                solver_team=MT,
                                pts=int(task["ap_reward"]),
                                task_title=f"{task['id']} · {task['title']}",
                                solver_label=username,
                            )
                            save_gs(gs)
                            
                            # Show success with clean celebration
                            st.markdown(f"""
                            <div style="background:linear-gradient(135deg,#00CC8833,#D4AF3733);border:2px solid #00CC88;border-radius:12px;padding:24px;text-align:center;box-shadow:0 0 40px rgba(0,204,136,0.4)">
                                <div style="font-family:Orbitron,monospace;font-size:1.8rem;color:#00CC88;margin-bottom:8px;text-shadow:0 0 20px #00CC8844">✓ SOLUTION VERIFIED</div>
                                <div style="font-family:'Share Tech Mono',monospace;font-size:1.1rem;color:var(--text);margin-bottom:12px">Token: <span style="color:#D4AF37;font-weight:bold">{token_or_msg}</span></div>
                                <div style="font-family:'Share Tech Mono',monospace;font-size:0.95rem;color:#00CC88">+{int(task['ap_reward'])} AP awarded</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.session_state["selected_bot_task"] = None
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(token_or_msg)

    # ─────────────────────────────────────────────────────────────
    # STRATEGY DECK
    # ─────────────────────────────────────────────────────────────
    elif active == "Strategy Deck":
        st.markdown('<div class="sec-lbl">🃏 ACTION CARDS · STRATEGY DECK</div>', unsafe_allow_html=True)

        all_teams = [t for t in teams.keys() if t != MT]
        alliances = gs.get("alliances", {}).get(MT, [])
        ally_reqs = gs.get("alliance_reqs", {}).get(MT, [])
        queued_actions = gs.get("queued_actions", {})
        my_queued = queued_actions.get(MT, None)
        my_attack_queue = [a for a in gs.get("queued_attacks", []) if a.get("actor") == MT]

        c1, c2, c3 = st.columns(3)

        # 1. Alliance Card
        with c1:
            st.markdown("""
            <div style="background:rgba(0, 204, 136, 0.05);border-top:2px solid #00CC88;padding:10px;height:100%">
            <h4 style="color:#00CC88;margin:0 0 10px 0;font-family:Orbitron">HANDSHAKE</h4>
            <div style="font-size:0.75rem;margin-bottom:10px;color:#aaa">Form a Non-Aggression Pact for strategic coordination.</div>
            <hr style="border-color:#00CC8844">
            """, unsafe_allow_html=True)
            if alliances:
                st.info(f"🤝 Currently allied with: **{alliances[0]}**")
            else:
                non_allies = [t for t in all_teams if t not in alliances]
                t_ally = st.selectbox("Offer Alliance to:", ["--"] + non_allies, key="ally_sel", label_visibility="collapsed")
                if st.button("SEND ALLIANCE REQUEST", use_container_width=True) and t_ally != "--":
                    if "alliance_reqs" not in gs:
                        gs["alliance_reqs"] = {}
                    if t_ally not in gs["alliance_reqs"]:
                        gs["alliance_reqs"][t_ally] = []
                    if MT not in gs["alliance_reqs"][t_ally]:
                        gs["alliance_reqs"][t_ally].append(MT)
                        save_gs(gs)
                        push_ev("SYS", f"Team {MT} offered an alliance to {t_ally}.", MT)
                        st.success("Request Sent!")

            if ally_reqs:
                st.markdown("<div style='margin-top:10px;font-size:0.8rem;color:#D4AF37'>PENDING REQUESTS</div>", unsafe_allow_html=True)
                for req_team in ally_reqs:
                    if st.button(f"ACCEPT {req_team}", key=f"acc_{req_team}", use_container_width=True):
                        # Make mutual - only one alliance at a time, replace existing
                        if "alliances" not in gs:
                            gs["alliances"] = {}
                        if MT not in gs["alliances"]:
                            gs["alliances"][MT] = []
                        if req_team not in gs["alliances"]:
                            gs["alliances"][req_team] = []

                        # Replace existing alliance with new one
                        gs["alliances"][MT] = [req_team]
                        gs["alliances"][req_team] = [MT]

                        gs["alliance_reqs"][MT].remove(req_team)
                        save_gs(gs)
                        push_ev("SYS", f"Team {MT} and {req_team} forged an Alliance!", MT)
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # 2. Backstab Card
        with c2:
            st.markdown("""
            <div style="background:rgba(255, 34, 68, 0.05);border-top:2px solid #FF2244;padding:10px;height:100%">
            <h4 style="color:#FF2244;margin:0 0 10px 0;font-family:Orbitron">BACKSTAB</h4>
            <div style="font-size:0.75rem;margin-bottom:10px;color:#aaa">Secretly override Alliance protection for the upcoming epoch rollover. Deals massive damage.</div>
            <hr style="border-color:#FF224444">
            """, unsafe_allow_html=True)
            if not alliances:
                st.info("You have no alliances.")
            else:
                t_bs = alliances[0]  # Only one alliance
                if st.button(f"QUEUE BACKSTAB vs {t_bs}", use_container_width=True):
                    if "queued_actions" not in gs:
                        gs["queued_actions"] = {}
                    gs["queued_actions"][MT] = {"action": "BACKSTAB", "target": t_bs}
                    save_gs(gs)
                    st.success("Backstab Queued!")

            if my_queued and my_queued["action"] == "BACKSTAB":
                st.warning(f"Queued secretly vs: {my_queued['target']}")
                if st.button("Cancel Queue", key="c_bs"):
                    gs["queued_actions"].pop(MT)
                    save_gs(gs)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # 3. Suspicion Card
        with c3:
            st.markdown("""
            <div style="background:rgba(0, 229, 255, 0.05);border-top:2px solid #00E5FF;padding:10px;height:100%">
            <h4 style="color:#00E5FF;margin:0 0 10px 0;font-family:Orbitron">SUSPICION</h4>
            <div style="font-size:0.75rem;margin-bottom:10px;color:#aaa">Investigate an ally. Resolves at rollover. Traitors are eliminated. False accusations eliminate YOU.</div>
            <hr style="border-color:#00E5FF44">
            """, unsafe_allow_html=True)
            if not alliances:
                st.info("You have no alliances.")
            else:
                t_susp = alliances[0]  # Only one alliance
                if st.button(f"QUEUE SUSPICION vs {t_susp}", use_container_width=True):
                    if "queued_actions" not in gs:
                        gs["queued_actions"] = {}
                    gs["queued_actions"][MT] = {"action": "SUSPICION", "target": t_susp}
                    save_gs(gs)
                    st.success("Suspicion Queued!")

            if my_queued and my_queued["action"] == "SUSPICION":
                st.warning(f"Queued vs: {my_queued['target']}")
                if st.button("Cancel Queue", key="c_susp"):
                    gs["queued_actions"].pop(MT)
                    save_gs(gs)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-lbl">⚔️ ATTACK QUEUE · EXECUTES AT EPOCH END</div>', unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:0.76rem;color:#aaa;margin-bottom:10px'>"
            f"Cost per hit: <b style='color:#00E5FF'>{ATTACK_COST_AP} AP</b> · "
            f"Damage per hit: <b style='color:#FF2244'>100 HP</b>. "
            f"Queue attacks in order. Execution is sequential at epoch rollover.</div>",
            unsafe_allow_html=True,
        )

        atk_col1, atk_col2, atk_col3 = st.columns([2, 1, 1], gap="small")
        with atk_col1:
            alive_targets = [t for t in all_teams if int(gs["hp"].get(t, 0)) > 0]
            target_team = st.selectbox("Target Team", alive_targets or ["--"], key="q_attack_target")
        with atk_col2:
            desired_hits = st.number_input("Hits", min_value=1, max_value=100, value=1, step=1, key="q_attack_hits")
        with atk_col3:
            st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
            if st.button("QUEUE ATTACK", use_container_width=True, disabled=not alive_targets):
                gs.setdefault("queued_attacks", []).append(
                    {
                        "id": str(uuid.uuid4()),
                        "actor": MT,
                        "target": target_team,
                        "hits": int(desired_hits),
                        "created": datetime.utcnow().isoformat(),
                    }
                )
                save_gs(gs)
                push_ev("SYS", f"{MT} queued {int(desired_hits)} hit(s) on {target_team} for epoch end.", MT)
                st.rerun()

        if my_attack_queue:
            st.markdown("<div style='font-size:0.8rem;color:#D4AF37;margin-top:8px'>YOUR QUEUED ATTACKS (IN ORDER)</div>", unsafe_allow_html=True)
            queued_cost = 0
            for idx, attack in enumerate(my_attack_queue, start=1):
                hits = int(attack.get("hits", 1) or 1)
                queued_cost += hits * ATTACK_COST_AP
                target = attack.get("target", "?")
                c_a, c_b = st.columns([4, 1], gap="small")
                with c_a:
                    st.markdown(
                        f"<div class='elim-row'><span>#{idx} → {target}</span>"
                        f"<span style='color:#00E5FF'>{hits} hit(s) · {hits * ATTACK_COST_AP} AP</span></div>",
                        unsafe_allow_html=True,
                    )
                with c_b:
                    attack_id = attack.get("id")
                    if st.button("Remove", key=f"rm_qatk_{attack_id}", use_container_width=True):
                        queue = gs.get("queued_attacks", [])
                        gs["queued_attacks"] = [a for a in queue if a.get("id") != attack_id]
                        save_gs(gs)
                        st.rerun()
            ap_now = int(gs["ap"].get(MT, 0))
            st.markdown(
                f"<div style='font-size:0.75rem;color:#aaa;margin-top:6px'>"
                f"Queued AP demand: <b style='color:#00E5FF'>{queued_cost}</b> · Current AP: <b style='color:#00E5FF'>{ap_now}</b>."
                f" Extra hits auto-skip at epoch end if AP is insufficient.</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-lbl">🌍 TERRITORIAL EXPANSION · CLAIM RANDOM ADJACENT CELL</div>', unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:0.76rem;color:#aaa;margin-bottom:10px'>"
            f"Cost: <b style='color:#00E5FF'>150 AP</b> per cell · Claims free cells closest to your territory for strategic expansion.</div>",
            unsafe_allow_html=True,
        )
        
        # Find unclaimed cells
        unclaimed_cells = [i for i, cell in enumerate(gs["grid"]) if not cell]
        
        # Find my adjacent unclaimed cells (cells next to my territory)
        my_cells = [i for i, cell in enumerate(gs["grid"]) if cell == MT]
        claimable_with_dist = []
        for other_idx in unclaimed_cells:
            # Find minimum distance to any of my cells (preference for closer cells)
            min_dist = min(abs(other_idx - my_idx) for my_idx in my_cells)
            if min_dist <= 5:  # Rough spatial proximity threshold
                claimable_with_dist.append((other_idx, min_dist))
        
        # Sort by distance (closest first) then randomize among closest
        claimable_unclaimed = [idx for idx, dist in claimable_with_dist]
        
        if not claimable_unclaimed:
            st.info("No unclaimed cells adjacent to your territory.")
        else:
            ap_now = int(gs["ap"].get(MT, 0))
            can_afford = ap_now >= 150
            
            if st.button("🎲 EXPAND TERRITORY (150 AP)", use_container_width=True, disabled=not can_afford):
                if can_afford and claimable_unclaimed:
                    import random
                    # Prioritize closer cells: weight selection towards those with smaller distance
                    weighted_cells = sorted(claimable_with_dist, key=lambda x: x[1])[:len(claimable_with_dist)//2+1]
                    selected_cell = random.choice([idx for idx, _ in weighted_cells])
                    gs["grid"][selected_cell] = MT
                    gs["ap"][MT] = ap_now - 150
                    save_gs(gs)
                    push_ev("SYS", f"{MT} claimed cell #{selected_cell}! Territory expanded.", MT)
                    st.success(f"✅ Successfully claimed cell #{selected_cell}!")
                    st.rerun()
                elif not can_afford:
                    st.error("❌ Insufficient AP (need 150).")


    # ─────────────────────────────────────────────────────────────
    # LEADERBOARD
    # ─────────────────────────────────────────────────────────────
    elif active == "Leaderboard":
        st.markdown('<div class="sec-lbl">🏆 KINGDOM RANKINGS · LIVE STANDINGS</div>', unsafe_allow_html=True)
        
        # Build leaderboard data
        leaderboard = []
        for tname, tinfo in teams.items():
            hp = int(gs["hp"].get(tname, STARTING_HP))
            ap = int(gs["ap"].get(tname, 0))
            terr = sum(1 for cell in gs["grid"] if cell == tname)
            members = len(tinfo.get("members", []))
            status = "🟢 ALIVE" if hp > 0 else "🔴 ELIMINATED"
            status_color = "#00CC88" if hp > 0 else "#FF2244"
            leaderboard.append({
                "team": tname,
                "color": tinfo.get("color", "#fff"),
                "icon": tinfo.get("icon", "·"),
                "hp": hp,
                "ap": ap,
                "territory": terr,
                "members": members,
                "status": status,
                "status_color": status_color,
            })
        
        # Sort by HP (descending)
        leaderboard_sorted = sorted(leaderboard, key=lambda x: x["hp"], reverse=True)
        
        # Header row
        st.markdown("""
        <div style="display:grid;grid-template-columns:0.4fr 1.5fr 1.5fr 1.5fr 1.2fr 1fr;gap:12px;margin-bottom:8px;padding:0 8px">
            <div style="font-family:'Orbitron',monospace;font-size:0.5rem;letter-spacing:2px;color:var(--dim);text-transform:uppercase">Rank</div>
            <div style="font-family:'Orbitron',monospace;font-size:0.5rem;letter-spacing:2px;color:var(--dim);text-transform:uppercase">Kingdom</div>
            <div style="font-family:'Orbitron',monospace;font-size:0.5rem;letter-spacing:2px;color:var(--dim);text-transform:uppercase">Health</div>
            <div style="font-family:'Orbitron',monospace;font-size:0.5rem;letter-spacing:2px;color:var(--dim);text-transform:uppercase">AP</div>
            <div style="font-family:'Orbitron',monospace;font-size:0.5rem;letter-spacing:2px;color:var(--dim);text-transform:uppercase">Territory</div>
            <div style="font-family:'Orbitron',monospace;font-size:0.5rem;letter-spacing:2px;color:var(--dim);text-transform:uppercase">Status</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display rankings as rows
        for rank, team_data in enumerate(leaderboard_sorted, start=1):
            hp_pct = max(0, min(100, team_data['hp'] / STARTING_HP * 100))
            status_symbol = "●" if "ALIVE" in team_data["status"] else "◆"
            
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:0.4fr 1.5fr 1.5fr 1.5fr 1.2fr 1fr;gap:12px;padding:10px 8px;background:rgba(212,175,55,0.02);border-bottom:1px solid rgba(212,175,55,0.08);border-radius:2px;align-items:center">
                <div style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;color:var(--gold);text-align:center">#{rank}</div>
                <div>
                    <div style="color:{team_data['color']};font-weight:700;font-family:'Share Tech Mono',monospace;font-size:0.85rem">{team_data['icon']} {team_data['team']}</div>
                    <div style="font-size:0.65rem;color:var(--dim);margin-top:2px">{team_data['members']} members</div>
                </div>
                <div>
                    <div style="color:{'#FF2244' if team_data['hp'] <= 1000 else team_data['color']};font-weight:700;font-family:'Share Tech Mono',monospace">{team_data['hp']:,} HP</div>
                    <div style="width:100%;height:4px;background:rgba(0,0,0,0.5);border-radius:1px;margin-top:4px;overflow:hidden">
                        <div style="width:{hp_pct}%;height:100%;background:linear-gradient(90deg,{team_data['color']},{'#FF2244' if team_data['hp'] <= 1000 else team_data['color']})"></div>
                    </div>
                </div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.9rem">
                    <div style="color:#00E5FF;font-weight:700">{team_data['ap']:,}</div>
                    <div style="font-size:0.65rem;color:var(--dim);margin-top:2px">AP</div>
                </div>
                <div style="text-align:center">
                    <div style="font-family:'Orbitron',monospace;font-size:1.2rem;color:var(--gold);font-weight:700">{team_data['territory']}</div>
                    <div style="font-size:0.65rem;color:var(--dim);margin-top:2px">cells</div>
                </div>
                <div style="text-align:center">
                    <div style="color:{team_data['status_color']};font-weight:700;font-family:'Share Tech Mono',monospace;font-size:0.75rem;letter-spacing:1px">{status_symbol} {team_data['status']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

