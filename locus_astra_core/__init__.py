"""
Locus Astra Core: Sovereign Neuro-Symbolic Agent Engine (v3.6.0-Astra)
Permanent Production Suite for Long-Horizon Autonomy, Tool Chaining,
OS Manipulation, and Grounded Research.
"""

from .chronos import LocusChronosSupervisor, LettaMemoryManager, Milestone
from .grammar import LocusGrammarEngine, StructuredToolCall
from .repo_indexer import LocusRepoIndexer, LocusRepoIndexer as ASTRepoIndexer
from .operator import WindowsUIABridge, SetOfMarksVisualEngine, LocusOperatorHTTPHandler, run_operator_server
from .researcher import DefuddleIngestionEngine, STORMPerspectiveGenerator, PaperQACitationVerifier

__version__ = "3.6.0-Astra"
__all__ = [
    "LocusChronosSupervisor",
    "LettaMemoryManager",
    "Milestone",
    "LocusGrammarEngine",
    "StructuredToolCall",
    "LocusRepoIndexer",
    "ASTRepoIndexer",
    "WindowsUIABridge",
    "SetOfMarksVisualEngine",
    "LocusOperatorHTTPHandler",
    "run_operator_server",
    "DefuddleIngestionEngine",
    "STORMPerspectiveGenerator",
    "PaperQACitationVerifier"
]
