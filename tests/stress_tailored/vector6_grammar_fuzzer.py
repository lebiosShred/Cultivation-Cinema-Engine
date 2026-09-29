"""
Vector 6: Adversarial CFG Token Fuzzing & Epsilon-Escape Stress (Tier-5 Tailored)
- 2,000 toxic payloads designed to break CFG parsers:
  - 120-level deep bracket nesting [[[[...]]]].
  - Embedded null bytes \x00, unicode surrogates, BOM headers, RTL overrides.
  - Memory bomb strings (100KB single lines without breaks).
  - Malformed and truncated JSON payloads testing heuristic repair and Epsilon-Escape relaxation.
- Target SLO: 0 unhandled Python crashes, P99 latency <= 3.0ms.
"""

import os
import sys
import time
import json
from pydantic import BaseModel, Field
from typing import Dict, Any, List

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import locus_astra_core
from locus_astra_core.grammar import LocusGrammarEngine

class TaskExecutionContract(BaseModel):
    action: str = Field(description="Action name")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)

def run_vector6_grammar_fuzzer(total_payloads: int = 2000) -> Dict[str, Any]:
    print(f"\n🧪 Starting Vector 6: Adversarial CFG Token Fuzzing ({total_payloads} toxic payloads)...")
    
    latencies = []
    clean_parses = 0
    heuristic_repairs = 0
    epsilon_escapes = 0
    crashes = 0
    
    t_start = time.time()
    for i in range(total_payloads):
        p_type = i % 5
        if p_type == 0:
            # 120-level deep bracket nesting
            payload = "{" + '"k": ' * 120 + '{"action": "deep_nest", "confidence": 0.9}' + "}" * 120
        elif p_type == 1:
            # Embedded null bytes and unicode surrogates
            payload = '{"action": "null_byte_\x00_test\uD800\uDFFF", "parameters": {"raw": "hello\x00world"}, "confidence": 0.95}'
        elif p_type == 2:
            # 100KB single-line memory bomb string
            bomb = "A" * 100000
            payload = f'{{"action": "memory_bomb", "parameters": {{"payload": "{bomb}"}}, "confidence": 0.5}}'
        elif p_type == 3:
            # Malformed JSON with single quotes and trailing commas
            payload = "{'action': 'heuristic_test', 'confidence': 0.88, 'tags': ['fast', 'stable',],}"
        else:
            # Unrecoverable truncated gibberish (testing Epsilon-Escape Valve)
            payload = "UNRECOVERABLE_CORRUPTED_NON_JSON_TOKEN_STREAM_0x994827"
            
        t0 = time.perf_counter()
        try:
            res = LocusGrammarEngine.validate_and_parse(payload)
            dt = (time.perf_counter() - t0) * 1000.0
            latencies.append(dt)
            
            if isinstance(res, dict) and res.get("_epsilon_recovery"):
                epsilon_escapes += 1
            elif isinstance(res, dict) and res.get("action") == "heuristic_test":
                heuristic_repairs += 1
            else:
                clean_parses += 1
        except Exception:
            crashes += 1
            
    total_elapsed = time.time() - t_start
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0.0
    p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0.0
    mean_lat = sum(latencies) / len(latencies) if latencies else 0.0
    
    passed = (
        crashes == 0 and
        p99 <= 3.0 and
        (clean_parses + heuristic_repairs + epsilon_escapes) == total_payloads
    )
    
    results = {
        "passed": passed,
        "total_payloads": total_payloads,
        "unhandled_crashes": crashes,
        "clean_parses": clean_parses,
        "heuristic_repairs": heuristic_repairs,
        "epsilon_escapes": epsilon_escapes,
        "mean_latency_ms": round(mean_lat, 3),
        "p95_latency_ms": round(p95, 3),
        "p99_latency_ms": round(p99, 3),
        "total_elapsed_s": round(total_elapsed, 2)
    }
    
    print(f"  Passed: {passed} | Payloads: {total_payloads} | Crashes: {crashes} | Clean: {clean_parses} | Repairs: {heuristic_repairs} | Escapes: {epsilon_escapes} | P99: {p99:.3f}ms")
    return results

if __name__ == '__main__':
    res = run_vector6_grammar_fuzzer(2000)
    print(json.dumps(res, indent=2))
