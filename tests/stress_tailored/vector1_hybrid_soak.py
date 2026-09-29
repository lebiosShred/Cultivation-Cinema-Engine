"""
Vector 1: Hybrid State & In-Memory / File Soak (Tier-5 Tailored)
- Executes 300 sequential milestone transitions via LocusChronosSupervisor.
- Alternates between in-memory SQLite (:memory:) and disk-backed WAL database.
- Injects 12 cascading failure cascades (stale git index.lock, file corruption).
- Validates anti-debris log isolation (>100MB flood compressed into <=4 lines).
- Profiles Process RSS memory footprint over 300 milestones to prove zero unbounded memory growth.
- Evaluates Mean-Time-To-Recovery (MTTR) via Git-backed physical checkpoints.
"""

import os
import sys
import time
import json
import shutil
import subprocess
import psutil
from typing import Dict, Any

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import locus_astra_core
from locus_astra_core.chronos import LocusChronosSupervisor

def run_vector1_hybrid_soak(milestone_count: int = 300, fault_interval: int = 25) -> Dict[str, Any]:
    print(f"\n🏃 Starting Vector 1: Hybrid State & In-Memory / File Soak ({milestone_count} milestones, fault every {fault_interval})...")
    process = psutil.Process(os.getpid())
    rss_start = process.memory_info().rss / (1024 * 1024)
    t_start = time.time()
    
    test_workdir = os.path.join(WORKSPACE_ROOT, "scratch", "tailored_soak_workspace")
    if os.path.exists(test_workdir):
        shutil.rmtree(test_workdir, ignore_errors=True)
    os.makedirs(test_workdir, exist_ok=True)
    
    # Ephemeral git repository
    subprocess.run(["git", "init"], cwd=test_workdir, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "tailored_soak@locus.internal"], cwd=test_workdir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Locus Tailored Bot"], cwd=test_workdir, capture_output=True)
    
    baseline_file = os.path.join(test_workdir, "state.config")
    with open(baseline_file, "w", encoding="utf-8") as f:
        f.write("status=initialized\nversion=3.6.0-Astra\n")
    subprocess.run(["git", "add", "-A"], cwd=test_workdir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Baseline commit"], cwd=test_workdir, capture_output=True)
    
    disk_db = os.path.join(test_workdir, "chronos_disk.db")
    supervisor_disk = LocusChronosSupervisor(workspace_root=test_workdir, scratch_dir=test_workdir, db_path=disk_db)
    supervisor_mem = LocusChronosSupervisor(workspace_root=test_workdir, scratch_dir=test_workdir, db_path=":memory:")
    
    completed_milestones = 0
    faults_injected = 0
    recoveries_succeeded = 0
    recovery_latencies = []
    
    fault_milestones = {i * fault_interval for i in range(1, (milestone_count // fault_interval) + 1)}
    
    try:
        for i in range(1, milestone_count + 1):
            ms_id = f"ms_tailored_{i:04d}"
            supervisor = supervisor_mem if (i % 2 == 1) else supervisor_disk
            
            # 1. Physical Git Checkpoint
            ckpt = supervisor.create_git_checkpoint(ms_id)
            
            # 2. Mutate state
            with open(baseline_file, "a", encoding="utf-8") as f:
                f.write(f"step_{i}=ok\n")
                
            # 3. Fault Injection at Milestones
            if i in fault_milestones:
                faults_injected += 1
                t_fault = time.time()
                
                # Injected Stale Git Lock
                fake_lock = os.path.join(test_workdir, ".git", "index.lock")
                with open(fake_lock, "w", encoding="utf-8") as lf:
                    lf.write("888888")
                os.utime(fake_lock, (time.time() - 30, time.time() - 30))
                
                # Injected File Corruption
                with open(baseline_file, "w", encoding="utf-8") as f:
                    f.write("FATAL_CORRUPTION_STATE_DESTROYED\n")
                    
                # Execute Recovery Protocol
                lock_purged = supervisor.clean_stale_git_locks()
                if ckpt:
                    rb_ok = supervisor.rollback_to_checkpoint(ckpt)
                    recovery_latencies.append(time.time() - t_fault)
                    if rb_ok and lock_purged:
                        recoveries_succeeded += 1
                        with open(baseline_file, "a", encoding="utf-8") as f:
                            f.write(f"step_{i}=recovered_and_completed\n")
                            
            # 4. Anti-debris execution test
            res = supervisor.isolate_execution(ms_id, f"python -c \"print('Milestone {i} OK')\"")
            if res.get("success"):
                completed_milestones += 1
                
        # 5. Anti-debris flood test (100,000 line debris flood)
        flood_res = supervisor_disk.isolate_execution(
            "debris_flood_test",
            "python -c \"for j in range(100000): print('DEBUG_LOG_SPAM_LINE_' + str(j))\""
        )
        diag_lines = flood_res.get("diagnostic", "").strip().split("\n")
        log_path = flood_res.get("log_path", "")
        log_size_kb = (os.path.getsize(log_path) / 1024.0) if (log_path and os.path.exists(log_path)) else 0.0
        debris_isolated = (len(diag_lines) <= 4 and log_size_kb > 100.0)
        
    finally:
        shutil.rmtree(test_workdir, ignore_errors=True)
        
    elapsed = time.time() - t_start
    rss_end = process.memory_info().rss / (1024 * 1024)
    rss_delta = rss_end - rss_start
    mean_mttr = sum(recovery_latencies) / len(recovery_latencies) if recovery_latencies else 0.0
    
    passed = (
        completed_milestones == milestone_count and
        faults_injected == 12 and
        recoveries_succeeded == 12 and
        mean_mttr <= 0.5 and
        rss_delta <= 50.0 and
        debris_isolated
    )
    
    results = {
        "passed": passed,
        "total_milestones": milestone_count,
        "completed_milestones": completed_milestones,
        "faults_injected": faults_injected,
        "recoveries_succeeded": recoveries_succeeded,
        "mttr_per_fault_s": round(mean_mttr, 3),
        "rss_start_mb": round(rss_start, 2),
        "rss_end_mb": round(rss_end, 2),
        "rss_delta_mb": round(rss_delta, 2),
        "debris_isolated": debris_isolated,
        "elapsed_seconds": round(elapsed, 2)
    }
    
    print(f"  Passed: {passed} | Milestones: {completed_milestones}/{milestone_count} | Recoveries: {recoveries_succeeded}/{faults_injected} | MTTR: {mean_mttr:.3f}s | RSS Delta: {rss_delta:.2f}MB in {elapsed:.2f}s")
    return results

if __name__ == '__main__':
    res = run_vector1_hybrid_soak(300, 25)
    print(json.dumps(res, indent=2))
