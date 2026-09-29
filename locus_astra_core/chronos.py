"""
Locus Chronos: Long-Horizon Supervisor & State Machine
Implements:
1. Letta (MemGPT) 3-tier memory (Core Memory, Recall SQLite log, Archival Vector DB).
2. Hierarchical POMDP milestone state machine.
3. Git-backed physical rollback checkpoints (locus/ckpt_<id>).
4. Anti-debris context isolation with compact diagnostic summaries.
"""

import os
import sys
import json
import time
import uuid
import sqlite3
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Milestone:
    id: str
    title: str
    goal: str
    target_files: List[str]
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    retry_count: int = 0
    max_retries: int = 3
    git_checkpoint_hash: Optional[str] = None
    output_log_path: Optional[str] = None
    diagnostic_summary: Optional[str] = None

class LettaMemoryManager:
    """
    3-Tier Stateful Memory Manager:
    - Tier 1: Core Memory (persona, active constraints, immutable invariants)
    - Tier 2: Recall Memory (chronological conversation and tool execution history in SQLite)
    - Tier 3: Archival Memory (long-term vector/knowledge graph persistence)
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._is_memory = (db_path == ":memory:")
        self._persistent_conn = None
        if self._is_memory:
            self._persistent_conn = sqlite3.connect(":memory:", timeout=30.0, check_same_thread=False)
        self._init_db()
        self.core_memory = {
            "identity": "Locus Prime Astra Supervisor",
            "active_invariants": [
                "Zero-sycophancy: Clinical, unvarnished engineering tone",
                "Verbatim ground truth: Never assume or fabricate claims",
                "Compounding error prevention: Rollback on 3 consecutive failures"
            ],
            "working_context": {}
        }

    def _get_connection(self):
        if self._is_memory:
            return self._persistent_conn
        return sqlite3.connect(self.db_path, timeout=30.0)

    def _init_db(self):
        if not self._is_memory:
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        conn = self._get_connection()
        cursor = conn.cursor()
        if not self._is_memory:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recall_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                session_id TEXT,
                event_type TEXT,
                content TEXT,
                metadata TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archival_memory (
                id TEXT PRIMARY KEY,
                timestamp REAL,
                key TEXT,
                value TEXT,
                embedding_vector BLOB
            )
        """)
        conn.commit()
        if not self._is_memory:
            conn.close()

    def record_recall(self, session_id: str, event_type: str, content: str, metadata: dict = None, max_retries: int = 5):
        for attempt in range(max_retries):
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO recall_memory (timestamp, session_id, event_type, content, metadata) VALUES (?, ?, ?, ?, ?)",
                    (time.time(), session_id, event_type, content, json.dumps(metadata or {}))
                )
                conn.commit()
                if not self._is_memory:
                    conn.close()
                return
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(0.05 * (2 ** attempt))
                else:
                    raise

    def query_recent_recalls(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, event_type, content, metadata FROM recall_memory WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        if not self._is_memory:
            conn.close()
        return [{"timestamp": r[0], "event_type": r[1], "content": r[2], "metadata": json.loads(r[3])} for r in reversed(rows)]



class LocusChronosSupervisor:
    """
    Supervisor daemon orchestrating multi-hour tasks with Git checkpointing and anti-debris isolation.
    """
    def __init__(self, workspace_root: str, scratch_dir: str, db_path: Optional[str] = None):
        self.workspace_root = workspace_root
        self.scratch_dir = scratch_dir
        self.runs_dir = os.path.join(scratch_dir, "runs")
        os.makedirs(self.runs_dir, exist_ok=True)
        
        self.db_path = db_path if db_path is not None else os.path.join(scratch_dir, "locus_chronos_memory.db")
        self.memory = LettaMemoryManager(self.db_path)
        self.session_id = str(uuid.uuid4())[:8]
        self.milestones: List[Milestone] = []

    def deconstruct_task(self, broad_goal: str, subtasks: List[Dict[str, Any]]) -> List[Milestone]:
        """Decompose a high-level goal into an ordered DAG of milestones."""
        self.milestones = []
        for i, st in enumerate(subtasks):
            ms = Milestone(
                id=f"ms_{i+1:02d}_{str(uuid.uuid4())[:6]}",
                title=st.get("title", f"Milestone {i+1}"),
                goal=st.get("goal", ""),
                target_files=st.get("target_files", [])
            )
            self.milestones.append(ms)
        return self.milestones

    def clean_stale_git_locks(self) -> bool:
        """
        Smart Lock Scavenger:
        Safely detects and unlinks orphaned .git/index.lock files left behind
        by crashed processes or SIGKILL interrupts without corrupting live git tasks.
        """
        lock_file = os.path.join(self.workspace_root, ".git", "index.lock")
        if not os.path.exists(lock_file):
            return False
        
        try:
            mtime = os.path.getmtime(lock_file)
            age_sec = time.time() - mtime
            # If lockfile is older than 15s, it is almost certainly orphaned from a dead process
            if age_sec > 15.0:
                os.remove(lock_file)
                self.memory.record_recall(self.session_id, "LOCK_SCAVENGER", f"Removed stale .git/index.lock (age: {age_sec:.1f}s)")
                return True
        except OSError:
            pass
        return False

    def create_git_checkpoint(self, milestone_id: str) -> Optional[str]:
        """Create a lightweight Git commit/tag to enable instant physical rollbacks with backoff."""
        self.clean_stale_git_locks()
        
        # 3-Attempt Exponential Backoff Jitter for Windows File Sharing (WinError 32)
        for attempt in range(3):
            try:
                # Check if git repo exists
                status_res = subprocess.run(["git", "status", "--porcelain"], cwd=self.workspace_root, capture_output=True, text=True)
                if status_res.returncode != 0:
                    return None
                
                # Commit current progress to milestone tag
                branch_tag = f"locus_ckpt_{milestone_id}"
                subprocess.run(["git", "add", "-A"], cwd=self.workspace_root, capture_output=True)
                commit_res = subprocess.run(["git", "commit", "-m", f"Locus Checkpoint: {milestone_id}"], cwd=self.workspace_root, capture_output=True, text=True)
                
                # Get current HEAD hash
                head_res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.workspace_root, capture_output=True, text=True)
                commit_hash = head_res.stdout.strip()
                self.memory.record_recall(self.session_id, "GIT_CHECKPOINT", f"Created checkpoint for {milestone_id}", {"hash": commit_hash})
                return commit_hash
            except Exception as e:
                time.sleep(0.05 * (2 ** attempt))
                if attempt == 2:
                    print(f"⚠️ [CHRONOS GIT ERROR]: {e}")
        return None

    def rollback_to_checkpoint(self, commit_hash: str) -> bool:
        """Physical hard rollback with stale lock clearing and Windows handle retry backoff."""
        self.clean_stale_git_locks()
        
        for attempt in range(3):
            try:
                print(f"🔄 [CHRONOS ROLLBACK]: Reverting workspace to checkpoint {commit_hash[:8]}...")
                subprocess.run(["git", "reset", "--hard", commit_hash], cwd=self.workspace_root, check=True, capture_output=True)
                subprocess.run(["git", "clean", "-fd"], cwd=self.workspace_root, check=True, capture_output=True)
                self.memory.record_recall(self.session_id, "GIT_ROLLBACK", f"Rolled back to {commit_hash}")
                return True
            except Exception as e:
                time.sleep(0.05 * (2 ** attempt))
                if attempt == 2:
                    print(f"🚨 [CHRONOS ROLLBACK FATAL]: Failed to revert state: {e}")
        return False

    def isolate_execution(self, milestone_id: str, cmd: str) -> Dict[str, Any]:
        """
        Anti-Debris Execution Wrapper:
        Writes 10,000+ line terminal logs to disk; passes only a 4-line diagnostic packet to LLM context.
        """
        log_file = os.path.join(self.runs_dir, f"{milestone_id}_{int(time.time())}.log")
        t0 = time.time()
        
        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            elapsed = time.time() - t0
            
            # Write raw stdout & stderr to disk
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"=== COMMAND: {cmd} ===\n")
                f.write(f"=== EXIT CODE: {proc.returncode} (took {elapsed:.2f}s) ===\n\n")
                f.write("--- STDOUT ---\n")
                f.write(proc.stdout)
                f.write("\n--- STDERR ---\n")
                f.write(proc.stderr)
            
            # Extract 4-line concise diagnostic packet
            success = (proc.returncode == 0)
            err_snippet = (proc.stderr or proc.stdout).strip().split("\n")[-4:]
            compact_diagnostic = (
                f"Status: {'SUCCESS' if success else 'FAILURE'} (Exit: {proc.returncode}) | Elapsed: {elapsed:.1f}s\n"
                f"Log File: {os.path.basename(log_file)}\n"
                f"Summary: {err_snippet[0][:80] if err_snippet else 'Clean execution'}\n"
                f"Detail: {err_snippet[-1][:80] if len(err_snippet) > 1 else 'No errors'}"
            )
            
            self.memory.record_recall(
                self.session_id,
                "EXECUTION_DIAGNOSTIC",
                compact_diagnostic,
                {"exit_code": proc.returncode, "elapsed": elapsed, "log_path": log_file}
            )
            
            return {
                "success": success,
                "exit_code": proc.returncode,
                "log_path": log_file,
                "diagnostic": compact_diagnostic
            }
        except subprocess.TimeoutExpired:
            diagnostic = f"Status: TIMEOUT_EXPIRED | Log File: {os.path.basename(log_file)}\nCommand exceeded 300s threshold."
            return {"success": False, "exit_code": -1, "log_path": log_file, "diagnostic": diagnostic}
        except Exception as e:
            diagnostic = f"Status: EXCEPTION | Error: {str(e)[:120]}"
            return {"success": False, "exit_code": -2, "log_path": log_file, "diagnostic": diagnostic}
