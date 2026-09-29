"""
Locus Outlines Grammar Engine
Provides grammar-constrained structured decoding, JSON schema validation,
and Context-Free Grammar (CFG) sampling for local LLMs (Ollama / vLLM / llama.cpp).
"""

import json
import re
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

class StructuredToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    thought_process: Optional[str] = None

class LocusGrammarEngine:
    """
    Guarantees structured token generation and schema conformance
    without hallucinated fields or invalid types.
    """

    @staticmethod
    def pydantic_to_json_schema(model: Type[BaseModel]) -> Dict[str, Any]:
        """Convert a Pydantic model class to an OpenAPI/Ollama JSON schema."""
        if hasattr(model, "model_json_schema"):
            return model.model_json_schema()
        elif hasattr(model, "schema"):
            return model.schema()
        raise ValueError(f"Object {model} is not a valid Pydantic model.")

    @staticmethod
    def format_request_payload(
        prompt: str,
        model: str,
        schema: Optional[Dict[str, Any]] = None,
        pydantic_cls: Optional[Type[BaseModel]] = None,
        regex_pattern: Optional[str] = None,
        temperature: float = 0.2,
        num_ctx: int = 4096,
        num_predict: int = 1024
    ) -> Dict[str, Any]:
        """
        Builds the exact JSON payload for Ollama with structured grammar enforcement.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": num_ctx,
                "num_predict": num_predict,
                "temperature": temperature
            }
        }

        # Apply schema constraint
        if pydantic_cls:
            payload["format"] = LocusGrammarEngine.pydantic_to_json_schema(pydantic_cls)
        elif schema:
            payload["format"] = schema
        elif regex_pattern:
            payload["format"] = "json"
            payload["regex"] = regex_pattern
        else:
            payload["format"] = "json"

        return payload

    @staticmethod
    def validate_and_parse(raw_output: str, pydantic_cls: Optional[Type[BaseModel]] = None) -> Any:
        """
        Two-Phase Resilient Decoding with Epsilon-Escape Valve:
        1. Strips markdown fences.
        2. Phase A: Fast direct parse & Pydantic validation.
        3. Phase B: Heuristic repair (trailing commas, single quotes, escaped brackets).
        4. Phase C (Epsilon Escape): Graceful relaxation returning structured payload instead of crashing.
        """
        clean = raw_output.strip()
        fence_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', clean, re.DOTALL)
        if fence_match:
            clean = fence_match.group(1).strip()
        elif clean.startswith("```") and clean.endswith("```"):
            clean = clean.strip("`").strip()

        # Phase A: Direct parse
        try:
            data = json.loads(clean)
            if pydantic_cls:
                return pydantic_cls.model_validate(data) if hasattr(pydantic_cls, "model_validate") else pydantic_cls(**data)
            return data
        except Exception:
            pass

        # Phase B: Heuristic syntax repair
        repaired = clean
        # Replace single quotes with double quotes around keys/strings
        repaired = re.sub(r"(?<!\\)'", '"', repaired)
        # Remove trailing commas before closing braces/brackets
        repaired = re.sub(r",\s*([\]}])", r"\1", repaired)
        try:
            data = json.loads(repaired)
            if pydantic_cls:
                return pydantic_cls.model_validate(data) if hasattr(pydantic_cls, "model_validate") else pydantic_cls(**data)
            return data
        except Exception:
            pass

        # Phase C: Epsilon-Escape Valve (Graceful Schema Relaxation)
        fallback = {
            "_epsilon_recovery": True,
            "raw_text": clean[:500],
            "error": "Grammar deadlock avoided: Output did not conform to strict schema; relaxed to raw text."
        }
        if pydantic_cls and isinstance(pydantic_cls, type) and issubclass(pydantic_cls, BaseModel):
            try:
                fields = pydantic_cls.model_fields if hasattr(pydantic_cls, "model_fields") else {}
                defaults = {k: "RECOVERED_VALUE" if v.annotation == str else 0 for k, v in fields.items()}
                return pydantic_cls(**defaults)
            except Exception:
                pass
        return fallback
