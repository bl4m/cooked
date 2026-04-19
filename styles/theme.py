"""
OVERTHRONE :: styles/theme.py
Neon cyberpunk grid aesthetic — reverted from new_update_given_by_team.
"""

FONTS = """@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');"""

_CSS = """
*, *::before, *::after { box-sizing: border-box; }
:root {
    --void:#03030a; --panel:#080813; --card:#0c0c1a; --gold:#D4AF37; --goldb:#FFD700;
    --cyan:#00E5FF; --red:#FF2244; --green:#00CC88; --purple:#CC44FF; --dim:#8890b8;
    --muted:#555a84; --text:#dde0ee; --bdim:rgba(255,255,255,0.05); --bgold:rgba(212,175,55,0.25);
}

.stApp {
    background-color:var(--void) !important;
    background-image:
        radial-gradient(ellipse 90% 50% at 50% 0%,rgba(0,150,255,0.07) 0%,transparent 55%),
        radial-gradient(ellipse 70% 60% at 95% 100%,rgba(212,175,55,0.05) 0%,transparent 50%),
        repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(255,255,255,0.012) 3px,rgba(255,255,255,0.012) 4px);
    font-family:'Rajdhani',sans-serif; color:var(--text) !important;
}

#MainMenu, footer, .stDeployButton, [data-testid="stFooter"], [data-testid="stMainMenu"], [data-testid="stDecoration"] { display: none !important; }
[data-baseweb="tab-list"] { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; height: 0 !important; min-height: 0 !important; overflow: visible !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="collapsedControl"] {
    display: flex !important; z-index: 9999 !important;
    background: rgba(212,175,55,0.15) !important;
    border: 1px solid rgba(212,175,55,0.4) !important;
    border-radius: 4px !important; color: #D4AF37 !important;
    position: fixed !important; top: 12px !important; left: 8px !important;
}
[data-testid="collapsedControl"]:hover { background: rgba(212,175,55,0.3) !important; }

.block-container { padding: 1rem 1rem 3rem !important; max-width:1700px !important; }
::-webkit-scrollbar { width:3px; height:3px; }
::-webkit-scrollbar-track { background:#06060f; }
::-webkit-scrollbar-thumb { background:var(--gold); border-radius:2px; }
[data-testid="stSidebar"] {
    background:linear-gradient(160deg,#05050f 0%,#09091a 100%) !important;
    border-right:1px solid rgba(212,175,55,0.2) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top:0 !important; }

.stButton > button {
    font-family:'Orbitron',monospace !important; font-size:0.58rem !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    background:transparent !important; border:1px solid rgba(212,175,55,0.3) !important;
    color:var(--gold) !important; border-radius:2px !important; padding:0.45rem 0.9rem !important;
    width:100%; transition:all 0.2s !important;
}
.stButton > button:hover { background:rgba(212,175,55,0.1) !important; box-shadow:0 0 16px rgba(212,175,55,0.18) !important; color:var(--goldb) !important; }
.stButton > button:disabled { opacity:0.35 !important; cursor:not-allowed !important; }
[data-testid="stSelectbox"] > div > div { background:var(--card) !important; border:1px solid rgba(212,175,55,0.25) !important; border-radius:2px !important; color:var(--text) !important; font-family:'Share Tech Mono',monospace !important; font-size:0.8rem !important; }
[data-testid="stTextInput"] input { background:var(--card) !important; border:1px solid rgba(212,175,55,0.25) !important; border-radius:2px !important; color:var(--text) !important; font-family:'Share Tech Mono',monospace !important; font-size:0.8rem !important; }
[data-testid="stTextArea"] textarea { background:#000 !important; border:1px solid rgba(0,229,255,0.3) !important; border-radius:2px !important; color:#00E5FF !important; font-family:'Share Tech Mono',monospace !important; font-size:0.82rem !important; }
[data-testid="stExpander"] { background:var(--card) !important; border:1px solid var(--bdim) !important; border-radius:3px !important; }
.stProgress > div > div > div { background:linear-gradient(90deg,var(--gold),var(--goldb)) !important; box-shadow:0 0 6px var(--gold) !important; }
.stProgress > div > div { background:rgba(212,175,55,0.08) !important; }
hr { border:none !important; border-top:1px solid rgba(212,175,55,0.15) !important; margin:0.8rem 0 !important; }

/* ── HEADER ────────────────────────────────────────────────── */
@keyframes scan  { from{transform:translateX(-100%)} to{transform:translateX(100%)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
.ot-hdr { display:flex;align-items:center;justify-content:space-between;padding:0.9rem 1.2rem;
    background:linear-gradient(90deg,rgba(212,175,55,0.05) 0%,transparent 70%);
    border-bottom:1px solid rgba(212,175,55,0.2);margin-bottom:1rem;position:relative;overflow:hidden; }
.ot-hdr::after { content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,var(--gold),transparent);animation:scan 4s linear infinite; }
.ot-logo { font-family:'Orbitron',monospace;font-size:1.9rem;font-weight:900;letter-spacing:6px;
    background:linear-gradient(135deg,#b8892a 0%,#FFD700 45%,#D4AF37 70%,#FFF5CC 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent; }
.ot-subtitle { font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:var(--dim);letter-spacing:3px;margin-top:2px; }
.ot-live-badge { font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--green);
    border:1px solid var(--green);padding:2px 8px;border-radius:2px;animation:pulse 1.8s ease infinite; }
.ot-epoch-box { text-align:right; }
.ot-epoch-num { font-family:'Orbitron',monospace;font-size:1.3rem;font-weight:700;color:var(--gold);line-height:1; }
.ot-epoch-phase { font-family:'Share Tech Mono',monospace;font-size:0.55rem;letter-spacing:3px;color:var(--dim); }
.ot-timer { font-family:'Orbitron',monospace;font-size:1.5rem;font-weight:700;min-width:75px;text-align:right; }
.ot-tbar { height:2px;background:var(--muted);margin-bottom:1rem;overflow:hidden; }
.ot-tbar-fill { height:100%;background:linear-gradient(90deg,var(--gold),var(--goldb));box-shadow:0 0 8px var(--gold); transition:width 1s linear; }

/* ── SIDEBAR COMPONENTS ────────────────────────────────────── */
.sb-head { padding:1rem;border-bottom:1px solid rgba(212,175,55,0.2); }
.sb-section { padding:0.9rem;border-bottom:1px solid var(--bdim); }
.sb-title { font-family:'Orbitron',monospace;font-size:0.5rem;letter-spacing:4px;color:#8a8ea8;margin-bottom:0.7rem; text-transform: uppercase; }
.sb-row { display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem; }
.sb-lbl { font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:var(--dim); text-transform: uppercase;}
.sb-val { font-family:'Share Tech Mono',monospace;font-size:0.68rem; }
.mini-bar { height:3px;background:var(--muted);border-radius:2px;margin-top:3px;overflow:hidden; }
.mini-bar-f { height:100%;border-radius:2px; }
.member-pill { display:inline-block;background:rgba(212,175,55,0.08);border:1px solid rgba(212,175,55,0.2);border-radius:2px;padding:1px 7px;font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#D4AF37;margin:2px; }

/* ── MAP ───────────────────────────────────────────────────── */
@keyframes safeZone { 0%,100%{opacity:0.5} 50%{opacity:1} }
@keyframes mapScan  { from{background-position:0 0} to{background-position:0 60px} }
.map-wrap {
    background:linear-gradient(135deg,#020d08 0%,#030f0a 40%,#020a06 100%);
    border:2px solid rgba(100,255,100,0.25); border-radius:6px;padding:10px;
    box-shadow:0 0 60px rgba(0,180,80,0.15),0 0 120px rgba(0,0,0,0.8),inset 0 0 80px rgba(0,0,0,0.6);
    position:relative;overflow:hidden;
}
.map-wrap::before {
    content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
    background-image:
        linear-gradient(rgba(0,255,80,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,80,0.025) 1px, transparent 1px);
    background-size:10% 10%; animation:mapScan 8s linear infinite;
}
.map-wrap > * { position:relative;z-index:1; }
.map-corner { position:absolute;width:18px;height:18px;border-color:rgba(100,255,100,0.5);border-style:solid;z-index:2; }
.map-corner.tl { top:4px;left:4px;border-width:2px 0 0 2px; }
.map-corner.tr { top:4px;right:4px;border-width:2px 2px 0 0; }
.map-corner.bl { bottom:4px;left:4px;border-width:0 0 2px 2px; }
.map-corner.br { bottom:4px;right:4px;border-width:0 2px 2px 0; }
.map-grid { display:grid;grid-template-columns:repeat(10,1fr);gap:2px;border:1px solid rgba(0,255,80,0.08);padding:3px; }
.map-cell { aspect-ratio:1;border-radius:2px;transition:all 0.25s cubic-bezier(.175,.885,.32,1.275);cursor:crosshair;position:relative; }
.map-cell:hover { transform:scale(1.7);z-index:10;filter:brightness(3) saturate(1.5);border-radius:3px; }
.map-cell.owned::after {
    content:'';position:absolute;inset:0;
    background:repeating-linear-gradient(45deg,transparent,transparent 2px,rgba(255,255,255,0.04) 2px,rgba(255,255,255,0.04) 4px);
    border-radius:2px;
}
.map-legend { display:flex;flex-wrap:wrap;gap:10px;margin-top:10px;padding-top:8px;border-top:1px solid rgba(0,255,80,0.1); }
.legend-item { display:flex;align-items:center;gap:6px;font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--dim); text-transform: uppercase;}
.legend-dot { width:10px;height:10px;border-radius:2px;flex-shrink:0; }

/* ── TABS AND CARDS ────────────────────────────────────────── */
.sec-lbl { font-family:'Orbitron',monospace;font-size:0.5rem;letter-spacing:4px;color:var(--dim);margin-bottom:8px; text-transform: uppercase;}
.tc { background:var(--card);border:1px solid var(--bdim);border-radius:3px;padding:0.9rem;position:relative;overflow:hidden;transition:border-color 0.3s;margin-bottom:8px; }
.tc:hover { border-color:rgba(212,175,55,0.3); }
.tc-diff { position:absolute;top:8px;right:8px;font-family:'Orbitron',monospace;font-size:0.45rem;letter-spacing:2px;padding:2px 7px;border-radius:1px; }
.tc-title { font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:1px;color:var(--gold);margin-bottom:0.4rem;margin-right:70px; }
.tc-desc  { font-size:0.78rem;color:var(--dim);line-height:1.5;margin-bottom:0.6rem; }
.tc-pts   { font-family:'Share Tech Mono',monospace;font-size:0.85rem;color:var(--cyan); }
.cd-bar { background:rgba(255,34,68,0.08);border:1px solid rgba(255,34,68,0.3);border-radius:3px;padding:0.6rem 0.9rem;font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#FF2244;margin-bottom:10px; }

@keyframes evIn  { from{opacity:0;transform:translateX(-6px)} to{opacity:1;transform:translateX(0)} }
.ev-feed { display:flex;flex-direction:column;gap:4px;max-height:300px;overflow-y:auto; }
.ev-item { padding:6px 10px;border-radius:2px;background:rgba(255,255,255,0.02);border-left:2px solid;display:flex;gap:8px;align-items:baseline;animation:evIn 0.3s ease-out;font-family:'Share Tech Mono',monospace;font-size:0.68rem; }
.ev-ts  { color:var(--muted);font-size:0.55rem;flex-shrink:0;white-space:nowrap; }
.ev-msg { color:var(--text); }
.elim-row { display:flex;justify-content:space-between;align-items:center;padding:5px 8px;border-bottom:1px solid var(--bdim);font-family:'Share Tech Mono',monospace;font-size:0.65rem; }

.code-term { background:#000810;border:1px solid rgba(0,229,255,0.25);border-radius:3px;padding:1rem;font-family:'Share Tech Mono',monospace;font-size:0.75rem;min-height:80px;overflow-y:auto;color:#00E5FF;white-space:pre-wrap; }
.code-term .stdout { color:#00E5FF; }
.code-term .stderr { color:#FF2244; }
.code-term .ok { color:#00CC88; }
/* Top Nav override active state for stButton */
.nav-tab-btn > button {
    border-color: rgba(212,175,55,0.1) !important;
    background: rgba(0,0,0,0.2) !important;
    color: var(--dim) !important;
}
.nav-tab-btn.active > button {
    border-color: var(--gold) !important;
    background: rgba(212,175,55,0.1) !important;
    color: var(--goldb) !important;
    box-shadow: 0 0 10px rgba(212,175,55,0.1) !important;
}

.warning-popup {
    background:rgba(255,34,68,0.15);
    border:2px dashed #FF2244;
    border-radius:4px;
    padding:1.5rem;
    text-align:center;
    margin-bottom:1.5rem;
    animation:pulse 2s ease infinite;
}
"""

def get_full_css() -> str:
    return f"<style>\n{FONTS}\n{_CSS}\n</style>"

def get_auth_css() -> str:
    return f"""<style>
{FONTS}
{_CSS}
[data-testid="stSidebar"] {{ display:none !important; }}
.block-container {{ max-width:600px !important; padding-top:4rem !important; }}
</style>"""
