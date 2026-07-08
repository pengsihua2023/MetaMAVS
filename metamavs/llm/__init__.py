"""Phase 4: optional LLM interpretation layer (local Gemma 4 E2B or Claude).

Backend is selected by the ``LLM_BACKEND`` env var: ``"gemma"`` (default, a local
OpenAI-compatible llama-server, no key) or ``"claude"`` (Anthropic, needs a key).

Entirely optional and additive — if the backend is unavailable (SDK missing, or
``llm.enabled`` is false, or the call fails), every entry point degrades to a
no-op and the deterministic Phase 1-3 pipeline is unchanged. No cloud key is ever
required to run MetaMAVS.
"""

from .client import active_model, generate, generate_json, llm_available, resolve_params

__all__ = ["active_model", "generate", "generate_json", "llm_available", "resolve_params"]
