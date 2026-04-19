"""
OVERTHRONE :: components/panels/tasks_panel.py
Tasks panel: Human tasks + Bot/Code tasks + Action cards — all in collapsible sections.
"""

import streamlit as st
import time
import random
from db import save_gs, push_ev
from config import TASKS, DIFF_COLOR, TASK_FAIL_CHANCE, ACTION_CARDS, TEAM_COLORS


def render_tasks_panel(gs, MT, dn):
    # ── HUMAN TASKS ───────────────────────────────────────────
    with st.expander("👑  MONARCH TASKS · HUMAN PUZZLES", expanded=True):
        st.markdown("""
        <div class="info-banner" style="background:rgba(0,229,255,0.04);border-left-color:#00E5FF;color:#8890b0">
            Logic puzzles, ciphers and riddles solved manually.
            Each correct answer earns AP for your kingdom.
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2, gap="small")
        for i, task in enumerate(TASKS["monarch"]):
            dc = DIFF_COLOR[task["diff"]]
            with (c1 if i % 2 == 0 else c2):
                _task_card(task, dc)
                if st.button(
                    f"CLAIM +{task['pts']} AP",
                    key=f"task_{task['id']}",
                    use_container_width=True,
                ):
                    _handle_task_claim(task, gs, MT, dn)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── BOT / CODE TASKS ──────────────────────────────────────
    with st.expander("🤖  SOVEREIGN TASKS · CODING CHALLENGES", expanded=False):
        st.markdown("""
        <div class="info-banner" style="background:rgba(153,51,255,0.06);border-left-color:#9933FF;color:#8890b0">
            Write and execute Python code to solve Sovereign challenges.
            Switch to the <span style="color:#9933FF">CODE TERMINAL</span> tab for the full editor with live output.
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2, gap="small")
        for i, task in enumerate(TASKS["sovereign"]):
            dc = DIFF_COLOR[task["diff"]]
            with (c1 if i % 2 == 0 else c2):
                _task_card(task, dc, title_color="#9933FF")
                from db import load_gs
                from _pages.war_room import _team_task_done
                live_gs = load_gs()
                task_solved = _team_task_done(live_gs, MT, task["id"])
                if task_solved:
                    st.markdown('<div style="color:#00CC88;font-size:0.72rem;margin-top:6px">✅ Completed by team</div>', unsafe_allow_html=True)
                else:
                    if st.button(
                        f"EXECUTE +{task['pts']} AP",
                        key=f"task_{task['id']}",
                        use_container_width=True,
                    ):
                        _handle_task_claim(task, gs, MT, dn, kind="TASK")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── ACTION CARDS inline ───────────────────────────────────
    with st.expander("⚔️  ACTION CARDS · BATTLE MOVES", expanded=False):
        st.markdown("""
        <div class="info-banner" style="background:rgba(255,34,68,0.05);border-left-color:#FF2244;color:#8890b0">
            Spend AP and play cards to attack, ally, betray or accuse.
            Every decision carries consequences on the battlefield.
        </div>
        """, unsafe_allow_html=True)
        other_teams = [t for t in TEAM_COLORS if t != MT]
        c1, c2 = st.columns(2, gap="small")
        for i, card in enumerate(ACTION_CARDS):
            with (c1 if i % 2 == 0 else c2):
                _action_card_mini(card)
                target = st.selectbox(
                    f"Target", other_teams,
                    key=f"inline_sel_{card['id']}",
                    label_visibility="collapsed",
                )
                if st.button(f"PLAY {card['id']}", key=f"inline_play_{card['id']}", use_container_width=True):
                    from components.panels.strategy_deck import _handle_card
                    _handle_card(card["id"], target, gs, MT, dn)


def _task_card(task: dict, dc: str, title_color: str = None):
    tc = title_color or "var(--gold)"
    st.markdown(f"""
    <div class="tc" style="border-top:2px solid {dc}55">
        <div class="tc-diff" style="background:{dc}18;color:{dc};border:1px solid {dc}44">{task['diff']}</div>
        <div class="tc-title" style="color:{tc}">{task['title']}</div>
        <div class="tc-desc">{task['desc']}</div>
        <div class="tc-pts">+{task['pts']} AP<span class="tc-pts-label">ATTACK POINTS</span></div>
    </div>
    """, unsafe_allow_html=True)


def _action_card_mini(card: dict):
    cc  = card["color"]
    cost_html = (
        f'<div class="ac-cost" style="color:{cc}99">Costs {card["cost"]} AP</div>'
        if card["cost"] else ""
    )
    st.markdown(f"""
    <div class="ac" style="border-top:2px solid {cc};padding:0.8rem">
        <div class="ac-top" style="background:linear-gradient(90deg,{cc},transparent)"></div>
        <span style="font-size:1.2rem">{card['icon']}</span>
        <div class="ac-label" style="color:{cc};margin-top:4px">{card['label']}</div>
        <div class="ac-desc">{card['desc']}</div>
        {cost_html}
    </div>
    """, unsafe_allow_html=True)



def _handle_task_claim(task: dict, gs: dict, MT: str, dn: str, kind: str = "TASK"):
    from db import load_gs
    from _pages.war_room import _mark_team_task_done, _team_task_done
    
    if random.random() < TASK_FAIL_CHANCE:
        push_ev(kind, f"Task FAILED — Team {MT}.", MT)
        st.error("❌ Task failed!")
    else:
        # Check if team already completed this task
        live_gs = load_gs()
        if _team_task_done(live_gs, MT, task["id"]):
            st.info("✓ Your team already completed this task.")
            st.rerun()
            return
        
        # Award AP and mark task as done
        gs["ap"][MT] = int(gs["ap"].get(MT, 0)) + task["pts"]
        _mark_team_task_done(gs, MT, task["id"])
        save_gs(gs)
        push_ev(kind, f"Team {MT} ({dn}) completed '{task['title']}' +{task['pts']} AP", MT)
        st.success(f"⚡ +{task['pts']} AP earned for {MT}!")
    st.rerun()
