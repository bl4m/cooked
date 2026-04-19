import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta

import streamlit as st

# Import config constants
try:
	from config import TEAM_PALETTE, EPOCH_DURATION_SECS, STARTING_HP, STARTING_AP
except ImportError:
	pass


class InMemoryStore:
	def __init__(self):
		self._kv = {}

	def get(self, key):
		return self._kv.get(key)

	def set(self, key, value, ex=None):
		self._kv[key] = value
		return True

	def lpush(self, key, *values):
		items = self._kv.get(key, [])
		if not isinstance(items, list):
			items = []
		for value in values:
			items.insert(0, value)
		self._kv[key] = items
		return len(items)

	def lrange(self, key, start, end):
		items = self._kv.get(key, [])
		if not isinstance(items, list):
			return []
		stop = None if end == -1 else end + 1
		return items[start:stop]

	def delete(self, key):
		self._kv.pop(key, None)
		return True

	def flushdb(self):
		self._kv.clear()
		return True

	def ping(self):
		return True


class SupabaseStore:
	def __init__(self, url: str, key: str, table: str = "ot_store"):
		from supabase import create_client

		self.client = create_client(url, key)
		self.table = table
		self._max_retries = 2
		self._retry_delay = 0.5  # seconds

	def _retry_operation(self, operation_func, operation_name="operation"):
		"""Execute operation with retry logic."""
		import time
		last_error = None
		for attempt in range(self._max_retries + 1):
			try:
				return operation_func()
			except Exception as e:
				last_error = e
				if attempt < self._max_retries:
					wait_time = self._retry_delay * (2 ** attempt)
					_LOG.warning(f"[DB] {operation_name} failed (attempt {attempt + 1}), retrying in {wait_time}s: {str(e)[:100]}")
					time.sleep(wait_time)
				else:
					_LOG.error(f"[DB] {operation_name} failed after {self._max_retries + 1} attempts: {str(e)[:100]}")
		raise last_error

	def _select_row(self, key: str):
		def _query():
			return (
				self.client.table(self.table)
				.select("key,value")
				.eq("key", key)
				.limit(1)
				.execute()
			)
		return self._retry_operation(_query, f"SELECT {key}")

	def get(self, key):
		try:
			res = self._select_row(key)
			data = res.data or []
			if not data:
				return None
			return data[0].get("value")
		except Exception as e:
			_LOG.error(f"[DB] get({key}) failed: {str(e)[:100]}")
			return None

	def set(self, key, value, ex=None):
		def _query():
			return self.client.table(self.table).upsert({"key": key, "value": value}).execute()
		try:
			self._retry_operation(_query, f"UPSERT {key}")
			return True
		except Exception as e:
			_LOG.error(f"[DB] set({key}) failed: {str(e)[:100]}")
			return False

	def lpush(self, key, *values):
		try:
			items = self.get(key)
			if not isinstance(items, list):
				items = []
			for value in values:
				items.insert(0, value)
			self.set(key, items)
			return len(items)
		except Exception as e:
			_LOG.error(f"[DB] lpush({key}) failed: {str(e)[:100]}")
			return 0

	def lrange(self, key, start, end):
		try:
			items = self.get(key)
			if not isinstance(items, list):
				return []
			stop = None if end == -1 else end + 1
			return items[start:stop]
		except Exception as e:
			_LOG.error(f"[DB] lrange({key}) failed: {str(e)[:100]}")
			return []

	def delete(self, key):
		def _query():
			return self.client.table(self.table).delete().eq("key", key).execute()
		try:
			self._retry_operation(_query, f"DELETE {key}")
			return True
		except Exception as e:
			_LOG.error(f"[DB] delete({key}) failed: {str(e)[:100]}")
			return False

	def flushdb(self):
		def _query():
			return self.client.table(self.table).delete().neq("key", "").execute()
		try:
			self._retry_operation(_query, "FLUSHDB")
			return True
		except Exception as e:
			_LOG.error(f"[DB] flushdb() failed: {str(e)[:100]}")
			return False

	def ping(self):
		def _query():
			return self.client.table(self.table).select("key").limit(1).execute()
		try:
			self._retry_operation(_query, "PING")
			return True
		except Exception as e:
			_LOG.error(f"[DB] ping() failed: {str(e)[:100]}")
			return False


@st.cache_resource
def get_store():
	global SUPABASE_LAST_ERROR
	global ACTIVE_DB_NAME
	global ACTIVE_DB_TABLE
	try:
		url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
		key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
		table = st.secrets.get("SUPABASE_TABLE", os.getenv("SUPABASE_TABLE", "ot_store"))
		if not url or not key:
			raise ValueError("SUPABASE_URL/SUPABASE_KEY not configured")
		store = SupabaseStore(url, key, table)
		store.ping()
		SUPABASE_LAST_ERROR = ""
		ACTIVE_DB_NAME = "SUPABASE"
		ACTIVE_DB_TABLE = table
		return store, True
	except Exception as exc:
		SUPABASE_LAST_ERROR = str(exc)
		ACTIVE_DB_NAME = "IN_MEMORY"
		ACTIVE_DB_TABLE = ""
		return InMemoryStore(), False


SUPABASE_LAST_ERROR = ""
ACTIVE_DB_NAME = "UNKNOWN"
ACTIVE_DB_TABLE = ""
R, supabase_live = get_store()
# Backward-compatible flag used by UI labels.
redis_live = supabase_live

_LOG = logging.getLogger(__name__)
if supabase_live:
	msg = f"[DB] backend={ACTIVE_DB_NAME} table={ACTIVE_DB_TABLE}"
	print(msg)
	_LOG.info(msg)
else:
	msg = f"[DB] backend={ACTIVE_DB_NAME} fallback_reason={SUPABASE_LAST_ERROR}"
	print(msg)
	_LOG.warning(msg)


# -- ACCOUNTS -------------------------------------------------
def hash_pw(pw):
	return hashlib.sha256(pw.encode()).hexdigest()


def load_users():
	raw = R.get("ot:users")
	if raw:
		try:
			return json.loads(raw)
		except Exception:
			pass
	return {}


def save_users(users):
	R.set("ot:users", json.dumps(users))


def get_user(username):
	return load_users().get(username)


def register_user(username, password, display_name):
	users = load_users()
	if username in users:
		return False, "Username exists."
	users[username] = {
		"pw_hash": hash_pw(password),
		"display_name": display_name,
		"team": None,
		"created": datetime.utcnow().isoformat(),
	}
	save_users(users)
	return True, "Account created"


def login_user(username, password):
	users = load_users()
	if username not in users:
		return False, "User not found."
	if users[username]["pw_hash"] != hash_pw(password):
		return False, "Wrong password."
	return True, users[username]


# -- DYNAMIC TEAMS -------------------------------------------
def load_teams():
	raw = R.get("ot:teams_meta")
	if raw:
		try:
			return json.loads(raw)
		except Exception:
			pass
	return {}


def save_teams(teams):
	R.set("ot:teams_meta", json.dumps(teams))


def load_teams_meta():
	return load_teams()


def create_team(tname, username, join_code=""):
	tname = tname.strip()
	teams = load_teams()
	users = load_users()
	if len(teams) >= 30:
		return False, "Maximum 30 teams allowed on the map."
	if tname in teams:
		return False, "Already exists."

	old_team = users.get(username, {}).get("team")
	if old_team and old_team in teams and username in teams[old_team]["members"]:
		teams[old_team]["members"].remove(username)

	idx = len(teams) % len(TEAM_PALETTE)
	col = TEAM_PALETTE[idx]

	teams[tname] = {
		"creator": username,
		"join_code": join_code,
		"members": [username],
		"created": datetime.utcnow().isoformat(),
		"color": col["color"],
		"bg": col["bg"],
		"icon": col["icon"],
	}
	save_teams(teams)

	users[username]["team"] = tname
	save_users(users)

	gs = load_gs()
	if tname not in gs["hp"]:
		gs["hp"][tname] = STARTING_HP
		gs["ap"][tname] = STARTING_AP

		empty_cells = [i for i, owner in enumerate(gs["grid"]) if not owner]
		if empty_cells:
			import random

			assigned = random.choice(empty_cells)
			gs["grid"][assigned] = tname

		save_gs(gs)

	return True, f"Created {tname}"


def join_team(tname, username, join_code=""):
	teams = load_teams()
	users = load_users()
	if tname not in teams:
		return False, "Kingdom not found."
	if str(teams[tname].get("join_code", "")) != str(join_code):
		return False, "Incorrect Vault Password."
	if username in teams[tname]["members"]:
		return False, "Already joined."

	old_team = users.get(username, {}).get("team")
	if old_team and old_team in teams and username in teams[old_team]["members"]:
		teams[old_team]["members"].remove(username)

	teams[tname]["members"].append(username)
	save_teams(teams)

	users[username]["team"] = tname
	save_users(users)
	return True, f"Joined {tname}"


# -- GAME STATE (GRID) ---------------------------------------
def _init_state():
	grid = [""] * 30
	return {
		"grid": grid,
		"hp": {},
		"ap": {},
		"epoch": 1,
		"phase": "MOBILIZATION",
		"epoch_end": (datetime.utcnow() + timedelta(seconds=EPOCH_DURATION_SECS)).isoformat(),
		"bypassed": {},
		"bots": {},
		"alliances": {},
		"alliance_reqs": {},
		"queued_actions": {},
		"task_done_by_user": {},  # Tracks completed tasks per username: {username: {task_id: timestamp}}
                "task_done_by_team": {},  # Tracks completed bot/sovereign tasks per team: {team: {task_id: timestamp}}
        }


def load_gs():
	raw = R.get("ot:state")
	if raw:
		try:
			return json.loads(raw)
		except Exception:
			pass
	state = _init_state()
	save_gs(state)
	return state


def save_gs(state):
	R.set("ot:state", json.dumps(state))


def reset_gs():
	R.delete("ot:state")


def push_ev(kind, msg, team=None):
	event = {"ts": datetime.utcnow().strftime("%H:%M:%S"), "kind": kind, "msg": msg, "team": team}
	R.lpush("ot:events", json.dumps(event))


def load_evs(limit=30):
	res = R.lrange("ot:events", 0, limit - 1)
	out = []
	for item in res:
		try:
			out.append(json.loads(item))
		except Exception:
			pass
	return out


def terr_count(grid, dict_teams=None):
	counts = {}
	if dict_teams:
		counts = {team: 0 for team in dict_teams}
	counts[""] = 0
	for cell in grid:
		if cell not in counts:
			counts[cell] = 0
		counts[cell] += 1
	return counts


def simulate_epoch(gs):
	# This project currently computes most epoch logic in the war_room page.
	gs = dict(gs)
	gs["epoch"] = int(gs.get("epoch", 0)) + 1
	gs["epoch_end"] = (datetime.utcnow() + timedelta(seconds=EPOCH_DURATION_SECS)).isoformat()
	return gs


def run_code_safe(code: str, timeout: int = 5) -> tuple[str, str]:
	blocked = [
		"import os",
		"import sys",
		"import subprocess",
		"open(",
		"__import__",
		"exec(",
		"eval(",
		"compile(",
		"os.system",
		"os.popen",
		"shutil",
	]
	for item in blocked:
		if item in code:
			return "", f"[SECURITY] Blocked: '{item}'"
	try:
		res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=timeout)
		return res.stdout[:3000], res.stderr[:1000]
	except subprocess.TimeoutExpired:
		return "", "[TIMEOUT] "
	except Exception as exc:
		return "", str(exc)


def run_bot_task(task_id: str, user_code: str, team: str, gs: dict) -> tuple[bool, str]:
	"""
	Orchestrator for bot task execution.
	
	VERIFY ONLY - does not apply AP rewards (handled by caller to support backstab/suspicion).
	
	Args:
		task_id: Task ID (e.g., "NA_06")
		user_code: User's Python code defining the required function
		team: Team ID
		gs: Game state dict
	
	Returns:
		(success: bool, message: str)
	"""
	import time
	from config import BOT_TASKS
	
	# Check if task exists
	if task_id not in BOT_TASKS:
		return False, f"Task {task_id} not found"
	
	task = BOT_TASKS[task_id]
	
	# Check if team already solved this task (per-team tracking)
	team_tasks = gs.get("task_done_by_team", {}).get(team, {})
	if task_id in team_tasks:
		return False, f"✅ Your team already solved {task_id}. No repeat submissions."
	
	# Check 30-second solve time limit per team
	now = time.time()
	solve_times = gs.setdefault("bot_solve_time", {})
	last_submit = solve_times.get(team, now - 35)
	time_remaining = int(30 - (now - last_submit))
	
	if now - last_submit < 30:
		return False, f"⏱️ Solve limit active: {time_remaining}s remaining. One submission per 30s."
	
	# Combine user code + test harness
	full_code = user_code + "\n" + task["test_harness"]
	
	# Run code safely
	stdout, stderr = run_code_safe(full_code, timeout=5)
	
	if stderr and "[SECURITY]" in stderr:
		return False, f"❌ {stderr}"
	
	if stderr and "[TIMEOUT]" in stderr:
		return False, f"❌ Code execution timeout (>5s)"
	
	if stderr:
		# Runtime error
		error_msg = stderr.split('\n')[0] if stderr else "Unknown error"
		return False, f"❌ Runtime error: {error_msg[:80]}"
	
	# Extract verify_val from stdout
	try:
		# The test harness computes verify_val
		# We need to extract it by executing the code and checking the result
		exec_globals = {}
		exec(full_code, exec_globals)
		verify_val = exec_globals.get("verify_val", None)
		
		if verify_val is None:
			return False, "❌ Test harness did not compute verify_val"
		
		expected = task["expected_output"]
		
		# Compare (with type tolerance for floats)
		if isinstance(expected, float) and isinstance(verify_val, (int, float)):
			match = abs(verify_val - expected) < 0.01
		else:
			match = verify_val == expected
		
		if not match:
			return False, f"❌ Wrong answer. Got: {verify_val}, Expected: {expected}"
		
		# Success! Mark as solved and update solve time (but AP is handled by caller)
		solve_times[team] = now
		from datetime import datetime
		gs.setdefault("task_done_by_team", {}).setdefault(team, {})[task_id] = datetime.utcnow().isoformat()
		
		return True, f"✅ {task['verify_token']}"
	
	except Exception as e:
		return False, f"❌ Verification error: {str(e)[:80]}"
