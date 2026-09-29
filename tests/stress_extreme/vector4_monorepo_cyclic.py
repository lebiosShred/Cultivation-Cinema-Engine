"""
Vector 4: High-Scale Monorepo Topology & Cyclic Symlink Attack
- Generates 10,000 synthetic multi-language source files (Python, TypeScript, Typst).
- Injects 10 recursive cyclic symlinks pointing back to parent roots.
- Injects 50 minified webpack bundles with 50,000-character single lines.
- Injects 50 syntactically corrupted source files.
- Evaluates LocusRepoIndexer AST traversal, symlink cycle breaker, and token budget ceiling.
"""

import os
import sys
import time
import json
import shutil
from typing import Dict, Any

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import locus_astra_core
from locus_astra_core.repo_indexer import LocusRepoIndexer

def run_vector4_monorepo_cyclic(file_count: int = 10000, target_budget: int = 1500) -> Dict[str, Any]:
    print(f"\n🗺️ Starting Vector 4: Monorepo Scale & Cyclic Attack ({file_count} synthetic files)...")
    
    fuzz_repo = os.path.join(WORKSPACE_ROOT, "scratch", "extreme_monorepo_repo")
    if os.path.exists(fuzz_repo):
        shutil.rmtree(fuzz_repo, ignore_errors=True)
    os.makedirs(fuzz_repo, exist_ok=True)
    
    t_gen_start = time.time()
    
    # 1. Generate 10,000 modular files across 50 packages
    packages = [f"pkg_{i:02d}" for i in range(50)]
    for pkg in packages:
        pkg_path = os.path.join(fuzz_repo, pkg)
        os.makedirs(pkg_path, exist_ok=True)
        
    files_per_pkg = file_count // len(packages)
    for pkg in packages:
        pkg_path = os.path.join(fuzz_repo, pkg)
        for j in range(files_per_pkg):
            ext = ".py" if j % 3 == 0 else (".ts" if j % 3 == 1 else ".typ")
            fpath = os.path.join(pkg_path, f"service_{j:03d}{ext}")
            
            if ext == ".py":
                content = f'''"""Service {j} in {pkg}."""
class Service{j}:
    def execute_{j}(self, param: int) -> str:
        return f"result_{j}"
'''
            elif ext == ".ts":
                content = f'''export interface IService{j} {{
    run(arg: number): string;
}}
export class ServiceImpl{j} implements IService{j} {{
    run(arg: number): string {{ return "res_{j}"; }}
}}
'''
            else:
                content = f'''#let service_{j}(title) = [
  == Service {j}: #title
]
'''
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
                
    # 2. Inject 50 Minified Webpack Traps (50,000 characters on line 1)
    minified_dir = os.path.join(fuzz_repo, "minified_traps")
    os.makedirs(minified_dir, exist_ok=True)
    for i in range(50):
        min_path = os.path.join(minified_dir, f"vendor_bundle_{i}.min.js")
        long_line = f"/* bundle {i} */ var a=" + ("x" * 50000) + ";console.log(a);"
        with open(min_path, "w", encoding="utf-8") as f:
            f.write(long_line)
            
    # 3. Inject 50 Corrupted Syntax Traps
    corrupt_dir = os.path.join(fuzz_repo, "syntax_traps")
    os.makedirs(corrupt_dir, exist_ok=True)
    for i in range(50):
        c_path = os.path.join(corrupt_dir, f"broken_{i}.py")
        with open(c_path, "w", encoding="utf-8") as f:
            f.write(f"def broken_{i}(x: unterminated string literal... \n    return {i} +++")
            
    # 4. Attempt 10 Cyclic Symlink Loops (where OS permissions allow)
    cyclic_links_created = 0
    for i in range(10):
        src_target = fuzz_repo
        link_dest = os.path.join(fuzz_repo, f"pkg_{i:02d}", f"cyclic_link_loop_{i}")
        try:
            os.symlink(src_target, link_dest, target_is_directory=True)
            cyclic_links_created += 1
        except (OSError, NotImplementedError):
            pass  # Windows unprivileged symlink policy fallback
            
    t_gen_elapsed = time.time() - t_gen_start
    print(f"  Generated {file_count} code files + 100 traps in {t_gen_elapsed:.2f}s (Cyclic symlinks created: {cyclic_links_created}).")
    
    # Run AST Indexing
    t_index_start = time.time()
    try:
        indexer = LocusRepoIndexer(fuzz_repo)
        files = indexer.scan_files()
        
        # Verify minified files were pruned
        minified_leaked = any("vendor_bundle_" in f for f in files)
        
        repo_map = indexer.build_repo_map(max_tokens=target_budget)
        generated_tokens = len(repo_map) // 4
        elapsed_index = time.time() - t_index_start
        throughput = round((file_count + 100) / max(0.001, elapsed_index), 1)
        
        # SLO Gates:
        # 1. Zero minified files leaked
        # 2. Token ceiling within budget (+ 150 buffer)
        # 3. Indexing time <= 3.0s (Throughput >= 3,000 files/sec)
        passed = (
            (not minified_leaked) and
            (generated_tokens <= target_budget + 150) and
            (elapsed_index <= 3.0) and
            (len(files) >= file_count)
        )
        
        return {
            "passed": passed,
            "total_files_generated": file_count + 100,
            "valid_files_scanned": len(files),
            "cyclic_symlinks_tested": cyclic_links_created,
            "minified_traps_pruned": not minified_leaked,
            "generated_tokens": generated_tokens,
            "token_budget_cap": target_budget,
            "indexing_time_s": round(elapsed_index, 3),
            "throughput_files_per_sec": throughput
        }
    finally:
        shutil.rmtree(fuzz_repo, ignore_errors=True)

if __name__ == "__main__":
    result = run_vector4_monorepo_cyclic()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)
