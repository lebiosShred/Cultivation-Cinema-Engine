"""
Vector 2: Massive Multi-Threaded WAL Saturation & Byzantine Kill (Tier-5 Tailored)
- 48 concurrent OS worker threads generating 15,000 mixed CRUD operations against SQLite WAL.
- Byzantine fault simulation: randomly 5% of operations simulate mid-write thread abortions.
- Measures throughput, lock collisions, and schema parsing errors.
- Executes PRAGMA integrity_check post-saturation.
"""

import os
import sys
import time
import json
import sqlite3
import random
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import locus_astra_core
from locus_astra_core.chronos import LettaMemoryManager

def run_vector2_wal_byzantine(num_workers: int = 48, ops_per_worker: int = 312) -> Dict[str, Any]:
    total_target_ops = num_workers * ops_per_worker
    print(f"\n⚡ Starting Vector 2: 48-Thread WAL Saturation & Byzantine Kill ({num_workers} threads, {ops_per_worker} ops/worker = {total_target_ops} total ops)...")
    
    test_db_dir = os.path.join(WORKSPACE_ROOT, "scratch", "tailored_wal_test")
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir, ignore_errors=True)
    os.makedirs(test_db_dir, exist_ok=True)
    test_db_path = os.path.join(test_db_dir, "wal_byzantine.db")
    
    # Initialize schema and WAL mode
    init_manager = LettaMemoryManager(db_path=test_db_path)
    init_manager.record_recall("system_init", "WAL_INIT", "WAL mode initialized")
    
    lock_errors = 0
    schema_errors = 0
    completed_ops = 0
    simulated_aborts = 0
    t_start = time.time()
    
    def worker_routine(worker_id: int):
        nonlocal lock_errors, schema_errors, completed_ops, simulated_aborts
        mem = LettaMemoryManager(db_path=test_db_path)
        local_completed = 0
        local_aborts = 0
        local_locks = 0
        local_schema = 0
        
        for op_idx in range(ops_per_worker):
            try:
                # 5% chance of simulated Byzantine mid-write failure
                if op_idx % 20 == 0:
                    local_aborts += 1
                    conn = None
                    try:
                        conn = mem._get_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO recall_memory (timestamp, session_id, event_type, content, metadata) VALUES (?, ?, ?, ?, ?)",
                            (time.time(), f"byzantine_sess_{worker_id}", "ABORTED", "aborted_content", "{}")
                        )
                        # Abrupt thread kill simulation before commit
                        raise RuntimeError("Simulated Byzantine worker thread termination")
                    except RuntimeError:
                        if conn:
                            conn.rollback()
                    finally:
                        if conn:
                            conn.close()
                    continue
                    
                action = op_idx % 3
                if action == 0:
                    mem.record_recall(f"worker_{worker_id}", "RECALL_WRITE", f"High frequency recall metric {op_idx}", {"op": op_idx})
                elif action == 1:
                    _ = mem.query_recent_recalls(f"worker_{worker_id}", limit=5)
                elif action == 2:
                    mem.record_recall(f"worker_{worker_id}", "STATE_TRANSITION", f"State transition checkpoint {op_idx}")
                local_completed += 1
            except sqlite3.OperationalError as oe:
                if "locked" in str(oe).lower():
                    local_locks += 1
            except Exception:
                local_schema += 1
                
        return local_completed, local_aborts, local_locks, local_schema
        
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(worker_routine, w_id) for w_id in range(num_workers)]
        for fut in as_completed(futures):
            c, a, l, s = fut.result()
            completed_ops += c
            simulated_aborts += a
            lock_errors += l
            schema_errors += s
            
    elapsed = time.time() - t_start
    throughput = round(completed_ops / elapsed, 1) if elapsed > 0 else 0.0
    
    # Verify B-tree integrity
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM recall_memory;")
    row_count = cursor.fetchone()[0]
    conn.close()
    
    shutil.rmtree(test_db_dir, ignore_errors=True)
    
    passed = (
        lock_errors == 0 and
        schema_errors == 0 and
        integrity.lower() == "ok" and
        completed_ops >= (total_target_ops * 0.90) and
        throughput >= 200.0
    )
    
    results = {
        "passed": passed,
        "workers": num_workers,
        "target_operations": total_target_ops,
        "completed_operations": completed_ops,
        "simulated_aborts": simulated_aborts,
        "lock_collision_errors": lock_errors,
        "schema_parse_errors": schema_errors,
        "b_tree_integrity": integrity,
        "persisted_rows": row_count,
        "elapsed_seconds": round(elapsed, 2),
        "throughput_ops_per_sec": throughput
    }
    
    print(f"  Passed: {passed} | Completed: {completed_ops}/{total_target_ops} ops | Aborts: {simulated_aborts} | Lock Collisions: {lock_errors} | B-Tree: {integrity} | Throughput: {throughput} ops/s in {elapsed:.2f}s")
    return results

if __name__ == '__main__':
    res = run_vector2_wal_byzantine(48, 312)
    print(json.dumps(res, indent=2))
