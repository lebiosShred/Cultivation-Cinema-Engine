"""
Locus Repo Indexer: AST Topological Codebase Map Generator
Inspired by Aider's repo-map architecture.
Compresses an entire multi-file project into a high-density, AST-grounded
structural map (classes, functions, parameters, docstrings, imports)
allowing the LLM to understand project topology without blowing context windows.
"""

import os
import ast
import re
from typing import List, Dict, Any, Optional

class LocusRepoIndexer:
    def __init__(self, workspace_root: str, max_file_size_kb: int = 250):
        self.workspace_root = os.path.abspath(workspace_root)
        self.max_file_size_bytes = max_file_size_kb * 1024
        self.ignore_dirs = {
            ".git", "node_modules", "__pycache__", ".venv", "venv",
            "dist", "build", ".next", ".cache", ".deliberate", ".system_generated"
        }
        self.supported_exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".typ"}

    def scan_files(self) -> List[str]:
        """Collect all relevant source files in the workspace with symlink cycle protection."""
        collected = []
        visited_realpaths = set()
        
        for root, dirs, files in os.walk(self.workspace_root, followlinks=True):
            # Smart Symlink Cycle Breaker
            real_root = os.path.realpath(root)
            if real_root in visited_realpaths:
                dirs[:] = []
                continue
            visited_realpaths.add(real_root)

            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs and not d.startswith(".")]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.supported_exts:
                    # Instant filename-based minified bundle pruning
                    if ".min." in file.lower() or "-min." in file.lower():
                        continue
                    collected.append(os.path.join(root, file))
        return sorted(collected)

    def parse_python_ast(self, file_path: str) -> Dict[str, Any]:
        """Extract top-level classes, methods, and functions with signatures."""
        symbols = {"classes": [], "functions": [], "imports": []}
        try:
            # File size guard (deferred to parse time)
            if os.path.getsize(file_path) > self.max_file_size_bytes:
                return symbols
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                first_line = f.readline()
                # Minified guard: skip files with lines > 1,000 chars
                if len(first_line) > 1000:
                    return symbols
                f.seek(0)
                content = f.read()
            tree = ast.parse(content)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    symbols["classes"].append({"name": node.name, "methods": methods})
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    params = [a.arg for a in node.args.args]
                    symbols["functions"].append({"name": node.name, "signature": f"{node.name}({', '.join(params)})"})
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    symbols["imports"].append(ast.dump(node))
        except Exception:
            pass
        return symbols

    def parse_js_ts_regex(self, file_path: str) -> Dict[str, Any]:
        """Fast regex signature extraction for JavaScript / TypeScript / JSX."""
        symbols = {"classes": [], "functions": [], "imports": []}
        try:
            # File size guard (deferred to parse time)
            if os.path.getsize(file_path) > self.max_file_size_bytes:
                return symbols
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                first_line = f.readline()
                if len(first_line) > 1000:
                    return symbols
                f.seek(0)
                content = f.read()

            for match in re.finditer(r'(?:export\s+)?class\s+([A-Za-z0-9_$]+)', content):
                symbols["classes"].append({"name": match.group(1), "methods": []})
            for match in re.finditer(r'(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\(([^)]*)\)', content):
                symbols["functions"].append({"name": match.group(1), "signature": f"{match.group(1)}({match.group(2).strip()})"})
            for match in re.finditer(r'(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>', content):
                symbols["functions"].append({"name": match.group(1), "signature": f"{match.group(1)}({match.group(2).strip()})"})
        except Exception:
            pass
        return symbols

    def build_repo_map(self, max_tokens: int = 1500) -> str:
        """Construct the dense, token-budgeted topological map."""
        files = self.scan_files()
        map_lines = ["# REPOSITORY TOPOLOGY MAP (AST Grounded)"]
        current_chars = len(map_lines[0])
        max_chars = max_tokens * 4
        
        for file_path in files:
            rel_path = os.path.relpath(file_path, self.workspace_root).replace("\\", "/")
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == ".py":
                syms = self.parse_python_ast(file_path)
            elif ext in {".js", ".ts", ".tsx", ".jsx"}:
                syms = self.parse_js_ts_regex(file_path)
            else:
                syms = {"classes": [], "functions": [], "imports": []}
            
            if not syms["classes"] and not syms["functions"]:
                entry_line = f"📄 {rel_path}"
                map_lines.append(entry_line)
                current_chars += len(entry_line) + 1
                if current_chars >= max_chars:
                    map_lines.append("  [... additional workspace symbols pruned for token budget ...]")
                    break
                continue
                
            file_entry = [f"📄 {rel_path}"]
            for c in syms["classes"][:5]:
                m_str = f" [{', '.join(c['methods'][:3])}]" if c['methods'] else ""
                file_entry.append(f"  ├─ class {c['name']}{m_str}")
            for fn in syms["functions"][:8]:
                file_entry.append(f"  ├─ fn {fn['signature']}")
            
            map_lines.extend(file_entry)
            current_chars += sum(len(line) + 1 for line in file_entry)
            
            if current_chars >= max_chars:
                map_lines.append("  [... additional workspace symbols pruned for token budget ...]")
                break

        return "\n".join(map_lines)

if __name__ == "__main__":
    indexer = LocusRepoIndexer(os.getcwd())
    print(indexer.build_repo_map(max_tokens=800))
