"""
Unit test suite for locus_astra_core package (v3.6.0-Astra).
Validates all 5 consolidated subsystems and physical hardenings.
"""

import unittest
import os
import sys

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import locus_astra_core
from pydantic import BaseModel

class SamplePayload(BaseModel):
    action: str
    target: str
    priority: int

class TestLocusAstraCore(unittest.TestCase):
    def test_01_version_and_exports(self):
        self.assertEqual(locus_astra_core.__version__, "3.6.0-Astra")
        self.assertTrue(len(locus_astra_core.__all__) >= 10)

    def test_02_letta_memory_wal_and_inmemory(self):
        mem = locus_astra_core.LettaMemoryManager(":memory:")
        mem.record_recall("session_unit", "TEST_EVENT", "Payload content", {"flag": True})
        recalls = mem.query_recent_recalls("session_unit")
        self.assertEqual(len(recalls), 1)
        self.assertEqual(recalls[0]["event_type"], "TEST_EVENT")
        self.assertEqual(recalls[0]["metadata"]["flag"], True)

    def test_03_grammar_engine_schema(self):
        schema = locus_astra_core.LocusGrammarEngine.pydantic_to_json_schema(SamplePayload)
        self.assertIn("properties", schema)
        self.assertIn("action", schema["properties"])
        
        # Test heuristic repair
        repaired = locus_astra_core.LocusGrammarEngine.validate_and_parse('{"action": "deploy", "target": "cloud", "priority": 1,}')
        self.assertEqual(repaired["action"], "deploy")

    def test_04_repo_indexer_topology(self):
        indexer = locus_astra_core.LocusRepoIndexer(WORKSPACE_ROOT)
        files = indexer.scan_files()
        self.assertTrue(any("chronos.py" in f for f in files))
        repo_map = indexer.build_repo_map(max_tokens=400)
        self.assertTrue(len(repo_map) > 50)

    def test_05_windows_uia_bridge(self):
        windows = locus_astra_core.WindowsUIABridge.list_open_windows()
        self.assertTrue(len(windows) > 0)
        self.assertIn("MainWindowTitle", windows[0])

    def test_06_paperqa_citation_verifier(self):
        verifier = locus_astra_core.PaperQACitationVerifier()
        corpus = "Document X: Model Alpha achieved 98.5% precision on Benchmark Beta in 2026."
        verifier.index_document("doc_x", corpus)
        
        # Valid claim
        res_valid = verifier.verify_claim("Model Alpha achieved 98.5% precision on Benchmark Beta")
        self.assertTrue(res_valid.get("verified"))
        
        # Poisoned metric
        res_fake_metric = verifier.verify_claim("Model Alpha achieved 42.0% precision on Benchmark Beta")
        self.assertFalse(res_fake_metric.get("verified"))
        
        # Fabricated entity
        res_fake_entity = verifier.verify_claim("Model Alpha achieved 98.5% precision on NonexistentOmega")
        self.assertFalse(res_fake_entity.get("verified"))

if __name__ == "__main__":
    unittest.main()
