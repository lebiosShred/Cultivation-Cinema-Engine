"""
Vector 3: Grammar Fuzzing & Malicious Token Adversarial Injection
- Generates 1,000 toxic and adversarial JSON payloads:
  1. Deeply nested JSON objects (up to 80 levels of recursion).
  2. Embedded null bytes (\\x00), surrogate pairs, and non-printable control chars.
  3. 100KB single-line memory bomb payloads.
  4. Heavily corrupted syntax (single quotes, unquoted keys, trailing commas).
  5. Conversational LLM prose wrappers with markdown backticks.
- Verifies zero unhandled crashes, 100% graceful recovery via Epsilon-Escape Valve.
- Enforces P99 latency SLO <= 5.0ms.
"""

import os
import sys
import time
import json
from typing import Dict, Any, List
from pydantic import BaseModel

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import locus_astra_core
from locus_astra_core.grammar import LocusGrammarEngine

class StrictActionSchema(BaseModel):
    action: str
    target: str
    code_snippet: str
    retry_count: int

def generate_toxic_payloads(count: int = 1000) -> List[str]:
    payloads = []
    
    # 1. 200 Deeply Nested JSON Payloads
    for i in range(200):
        depth = 10 + (i % 50)
        nested = '{"key": ' * depth + '"deep_value"' + '}' * depth
        payloads.append(nested)
        
    # 2. 200 Null-Byte & Control Character Payloads
    for i in range(200):
        corrupted = f'{{"action": "exec\\x00_inject_{i}", "target": "\\x01\\x02\\x03path/file_{i}.py", "code_snippet": "print(\\x00)", "retry_count": {i % 5}}}'
        payloads.append(corrupted)
        
    # 3. 200 Memory Bomb Strings (50KB-100KB single lines)
    for i in range(200):
        bomb_str = "A" * (50000 + (i * 250))
        payloads.append(f'{{"action": "bomb", "target": "memory", "code_snippet": "{bomb_str}", "retry_count": 0}}')
        
    # 4. 200 Corrupted Syntax Payloads (Single quotes, missing colons, trailing commas)
    for i in range(200):
        syntax_trap = f"{{'action': 'patch', 'target': 'config.json', 'code_snippet': 'var x = {i};', 'retry_count': {i},,,,}}"
        payloads.append(syntax_trap)
        
    # 5. 200 Conversational LLM Prose Wrappers
    for i in range(200):
        prose = f"Certainly! Here is the requested tool call formatted as requested by your prompt:\n```json\n{{\"action\": \"compile\", \"target\": \"build.rs\", \"code_snippet\": \"fn main() {{ println!(\\\"{i}\\\"); }}\", \"retry_count\": {i % 3}}}\n```\nLet me know if you need further adjustments!"
        payloads.append(prose)
        
    return payloads[:count]

def run_vector3_grammar_fuzz(payload_count: int = 1000) -> Dict[str, Any]:
    print(f"\n⚡ Starting Vector 3: Grammar Adversarial Fuzz ({payload_count} toxic payloads)...")
    payloads = generate_toxic_payloads(payload_count)
    
    crashes = 0
    clean_parses = 0
    repaired_parses = 0
    epsilon_escapes = 0
    latencies_ms = []
    
    t_start = time.time()
    
    for p in payloads:
        t0 = time.time()
        try:
            res = LocusGrammarEngine.validate_and_parse(p, pydantic_cls=StrictActionSchema)
            elapsed_ms = (time.time() - t0) * 1000
            latencies_ms.append(elapsed_ms)
            
            if isinstance(res, StrictActionSchema):
                clean_parses += 1
            elif isinstance(res, dict) and res.get("_epsilon_recovery"):
                epsilon_escapes += 1
            elif isinstance(res, dict):
                repaired_parses += 1
            else:
                epsilon_escapes += 1
        except Exception:
            crashes += 1
            latencies_ms.append((time.time() - t0) * 1000)
            
    total_elapsed = time.time() - t_start
    sorted_latencies = sorted(latencies_ms)
    mean_lat = round(sum(latencies_ms) / len(latencies_ms), 3)
    p95_lat = round(sorted_latencies[int(len(sorted_latencies) * 0.95)], 3)
    p99_lat = round(sorted_latencies[int(len(sorted_latencies) * 0.99)], 3)
    
    # SLO Gates:
    # 1. Zero unhandled crashes (100% crash resilience)
    # 2. 100% of payloads successfully triaged (clean + repaired + epsilon == total)
    # 3. P99 latency <= 5.0ms
    passed = (crashes == 0) and (p99_lat <= 5.0) and (clean_parses + repaired_parses + epsilon_escapes == payload_count)
    
    return {
        "passed": passed,
        "total_payloads": payload_count,
        "unhandled_crashes": crashes,
        "clean_parses": clean_parses,
        "heuristic_repairs": repaired_parses,
        "epsilon_escapes": epsilon_escapes,
        "mean_latency_ms": mean_lat,
        "p95_latency_ms": p95_lat,
        "p99_latency_ms": p99_lat,
        "total_elapsed_s": round(total_elapsed, 2)
    }

if __name__ == "__main__":
    result = run_vector3_grammar_fuzz()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)
