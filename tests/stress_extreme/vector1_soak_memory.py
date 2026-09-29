"""
Vector 1: Deep Long-Horizon Soak & Memory Footprint Profiling
- Executes 250 sequential milestones via LocusChronosSupervisor.
- Injects 10 distinct failure cascades (simulated disk corruption, stale locks).
- Measures Process RSS memory footprint over time to guarantee zero unbounded memory growth.
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

def run_vector1_soak(milestone_count: int = 250, fault_interval: int = 25) -> Dict[str, Any]:
    print(f"\n🏃 Starting Vector 1: Extreme Soak ({milestone_count} milestones, fault every {fault_interval})...")
    process = psutil.Process(os.getpid())
    rss_start = process.memory_info().rss / (1024 * 1024)
    t_start = time.time()
    
    test_workdir = os.path.join(WORKSPACE_ROOT, "scratch", "extreme_soak_workspace")
    if os.path.exists(test_workdir):
        shutil.rmtree(test_workdir, ignore_errors=True)
    os.makedirs(test_workdir, exist_ok=True)
    
    # Initialize ephemeral git repository
    subprocess.run(["git", "init"], cwd=test_workdir, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "soak@locus.internal"], cwd=test_workdir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Locus Extreme Bot"], cwd=test_workdir, capture_output=True)
    
    # Baseline configuration file
    baseline_file = os.path.join(test_workdir, "state.config")
    with open(baseline_file, "w") as f:
        f.write("status=initialized\nversion=3.6.0\n")
    subprocess.run(["git", "add", "-A"], cwd=test_workdir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Baseline commit"], cwd=test_workdir, capture_output=True)
    
    supervisor = LocusChronosSupervisor(workspace_root=test_workdir, scratch_dir=test_workdir)
    
    completed_milestones = 0
    faults_injected = 0
    recoveries_succeeded = 0
    recovery_latencies = []
    
    fault_milestones = {i * fault_interval for i in range(1, (milestone_count // fault_interval) + 1)}
    
    try:
        for i in range(1, milestone_count + 1):
            ms_id = f"ms_ext_{i:04d}"
            
            # 1. Create Git physical checkpoint
            ckpt = supervisor.create_git_checkpoint(ms_id)
            
            # 2. Progress state
            with open(baseline_file, "a") as f:
                f.write(f"step_{i}=ok\n")
                
            # 3. Simulate Failure Cascade
            if i in fault_milestones:
                faults_injected += 1
                t_fault = time.time()
                
                # Injected Stale Git Lock
                fake_lock = os.path.join(test_workdir, ".git", "index.lock")
                with open(fake_lock, "w") as lf:
                    lf.write("999999")
                os.utime(fake_lock, (time.time() - 30, time.time() - 30))
                
                # Injected Fatal Disk Corruption
                with open(baseline_file, "w") as f:
                    f.write("FATAL_CORRUPTION_STATE_DESTROYED\n")
                    
                # Execute Recovery Protocol
                lock_purged = supervisor.clean_stale_git_locks()
                if ckpt:
                    rb_ok = supervisor.rollback_to_checkpoint(ckpt)
                    recovery_latencies.append(time.time() - t_fault)
                    if rb_ok and lock_purged:
                        recoveries_succeeded += 1
                        # Re-commit valid state after recovery
                        with open(baseline_file, "a") as f:
                            f.write(f"step_{i}=recovered_and_completed\n")
                            
            # 4. Anti-debris execution
            res = supervisor.isolate_execution(ms_id, f"python -c \"print('Milestone {i} OK')\"")
            if res.get("success"):
                completed_milestones += 1
                
    finally:
        shutil.rmtree(test_workdir, ignore_errors=True)
        
    elapsed = time.time() - t_start
    rss_end = process.memory_info().rss / (1024 * 1024)
    rss_delta = round(rss_end - rss_start, 2)
    mean_recovery = round(sum(recovery_latencies) / max(1, len(recovery_latencies)), 3)
    
    # SLO Gates:
    # 1. All 250 milestones executed
    # 2. All 10 recoveries succeeded
    # 3. RSS memory growth <= 50MB
    # 4. Mean recovery time <= 5.0s
    passed = (
        (completed_milestones == milestone_count) and
        (recoveries_succeeded == len(fault_milestones)) and
        (rss_delta <= 50.0) and
        (mean_recovery <= 5.0)
    )
    
    return {
        "passed": passed,
        "total_milestones": milestone_count,
        "completed_milestones": completed_milestones,
        "faults_injected": faults_injected,
        "recoveries_succeeded": recoveries_succeeded,
        "mttr_per_fault_s": mean_recovery,
        "rss_start_mb": round(rss_start, 2),
        "rss_end_mb": round(rss_end, 2),
        "rss_delta_mb": rss_delta,
        "elapsed_seconds": round(elapsed, 2)
    }

if __name__ == "__main__":
    result = run_vector1_soak()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)
