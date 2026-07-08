"""Thin, defensive wrapper around the project's LLM backend.

Supports two interchangeable backends selected by the ``LLM_BACKEND`` env var:

- ``"gemma"`` (default): a local, OpenAI-compatible server (llama-server serving
  Gemma 4 E2B). No API key required.
- ``"claude"``: the Anthropic Claude API (needs ``ANTHROPIC_API_KEY``).

Loads the key/URL from a project ``.env`` (or the environment), and never raises
into the workflow: any missing-key / SDK / API failure returns ``None`` so the
caller falls back to deterministic behaviour.
"""

from __future__ import annotations

import json
import os
import re

from ..utils.logging_utils import get_logger

logger = get_logger("llm.client")

# Default per the claude-api guidance: latest Opus, adaptive thinking.
DEFAULT_MODEL = "claude-opus-4-8"

# Local Gemma (llama-server) defaults; overridable via env.
DEFAULT_BACKEND = "gemma"
GEMMA_BASE_URL = "http://localhost:8080/v1"
GEMMA_MODEL = "gemma-4-E2B-it"
GEMMA_API_KEY = "not-needed"  # llama-server ignores it but the SDK requires non-empty
# Gemma 4 E2B is a reasoning model: it spends output tokens on hidden reasoning
# before the visible answer. Guarantee headroom so short-budget agents (e.g. qc)
# still get non-empty content after the reasoning tokens.
GEMMA_MIN_MAX_TOKENS = 2048


def _load_env() -> None:
    """Load .env (if python-dotenv is installed) so backend env vars are set."""

    try:
        from dotenv import load_dotenv

        # override=True so a project .env key takes precedence over any key
        # already exported in the shell environment.
        load_dotenv(override=True)
    except Exception:
        pass  # dotenv optional; env vars may already be set


def _backend() -> str:
    """Return the selected LLM backend ('gemma' or 'claude')."""

    _load_env()
    return os.getenv("LLM_BACKEND", DEFAULT_BACKEND).strip().lower()


def resolve_params(llm_cfg: dict | None, agent: str) -> dict:
    """Resolve ``{model, effort, max_tokens}`` for ``agent`` from an llm config dict.

    Applies any per-agent override in ``llm_cfg['overrides'][agent]`` over the
    top-level ``llm.*`` values; falls back to library defaults if absent. ``agent``
    is one of: qc, taxonomy, abundance, novel_virus, risk_assessment,
    llm_interpretation.

    Note: the resolved ``model`` is used verbatim by the Claude backend. Under the
    Gemma backend the model string is a no-op (llama-server serves one model);
    ``generate`` substitutes the configured Gemma model.
    """

    llm_cfg = llm_cfg or {}
    override = (llm_cfg.get("overrides") or {}).get(agent) or {}
    return {
        "model": override.get("model") or llm_cfg.get("model") or DEFAULT_MODEL,
        "effort": override.get("effort") or llm_cfg.get("effort") or "medium",
        "max_tokens": int(override.get("max_tokens") or llm_cfg.get("max_tokens") or 4000),
    }


def active_model(configured_model: str | None = None) -> str:
    """Return the model string actually used by the selected backend.

    Under the Gemma backend the configured (Claude) model is a no-op, so report
    the real served model instead; under Claude, echo the configured model.
    """

    if _backend() == "gemma":
        return os.getenv("GEMMA_MODEL", GEMMA_MODEL)
    return configured_model or DEFAULT_MODEL


def llm_available() -> bool:
    """True if the selected backend's SDK (and key, for Claude) are present."""

    backend = _backend()
    if backend == "gemma":
        try:
            import openai  # noqa: F401
        except Exception:
            return False
        return True
    if backend == "claude":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return False
        try:
            import anthropic  # noqa: F401
        except Exception:
            return False
        return True
    logger.warning("Unknown LLM_BACKEND=%r — treating LLM as unavailable", backend)
    return False


def _generate_gemma(
    system: str,
    user: str,
    *,
    max_tokens: int,
    effort: str,
    cached_prefix: str | None,
) -> str | None:
    """Generate via the local OpenAI-compatible server (Gemma 4 E2B)."""

    from openai import OpenAI

    base_url = os.getenv("GEMMA_BASE_URL", GEMMA_BASE_URL)
    model = os.getenv("GEMMA_MODEL", GEMMA_MODEL)
    api_key = os.getenv("GEMMA_API_KEY", GEMMA_API_KEY)

    # OpenAI chat API has no separate cache breakpoint; fold the shared reference
    # into the system message. llama-server still prefix-caches it automatically.
    sys_text = f"{cached_prefix}\n\n{system}" if cached_prefix else system
    # Reasoning tokens count against max_tokens; enforce a floor so content survives.
    budget = max(int(max_tokens), GEMMA_MIN_MAX_TOKENS)

    client = OpenAI(base_url=base_url, api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_text},
            {"role": "user", "content": user},
        ],
        max_tokens=budget,
        temperature=0.3,
    )
    choice = resp.choices[0]
    text = (choice.message.content or "").strip()
    usage = getattr(resp, "usage", None)
    n_in = getattr(usage, "prompt_tokens", 0) if usage else 0
    n_out = getattr(usage, "completion_tokens", 0) if usage else 0
    logger.info("LLM ok (gemma:%s): %d in, %d out, finish=%s",
                model, n_in, n_out, choice.finish_reason)
    if not text:
        logger.warning("Gemma returned empty content (finish=%s) — likely reasoning "
                       "consumed the token budget; falling back", choice.finish_reason)
    return text or None


def _generate_claude(
    system: str,
    user: str,
    *,
    model: str,
    effort: str,
    max_tokens: int,
    use_thinking: bool,
    cached_prefix: str | None,
) -> str | None:
    """Generate via the Anthropic Claude API."""

    import anthropic

    client = anthropic.Anthropic()
    if cached_prefix:
        system_blocks = [
            {"type": "text", "text": cached_prefix, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": system},
        ]
    else:
        system_blocks = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_blocks,
        "messages": [{"role": "user", "content": user}],
    }
    if use_thinking:
        kwargs["thinking"] = {"type": "adaptive"}
        kwargs["output_config"] = {"effort": effort}

    resp = client.messages.create(**kwargs)
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    cr = getattr(resp.usage, "cache_read_input_tokens", 0)
    logger.info("LLM ok (claude:%s): %d in, %d out, %d cache-read",
                model, resp.usage.input_tokens, resp.usage.output_tokens, cr)
    return text or None


def generate(
    system: str,
    user: str,
    *,
    model: str = DEFAULT_MODEL,
    effort: str = "medium",
    max_tokens: int = 4000,
    use_thinking: bool = True,
    cached_prefix: str | None = None,
) -> str | None:
    """Generate text from the selected backend, or None on any failure / no key.

    If ``cached_prefix`` is given (e.g. a large shared reference) it is placed
    first so it is reused via prompt caching (an explicit breakpoint on Claude,
    automatic prefix caching on llama-server). The agent-specific ``system``
    follows it; the per-run ``user`` content stays uncached.
    """

    if not llm_available():
        logger.info("LLM not available (backend=%s) — skipping interpretation", _backend())
        return None

    backend = _backend()
    try:
        if backend == "gemma":
            return _generate_gemma(
                system, user,
                max_tokens=max_tokens, effort=effort, cached_prefix=cached_prefix,
            )
        return _generate_claude(
            system, user,
            model=model, effort=effort, max_tokens=max_tokens,
            use_thinking=use_thinking, cached_prefix=cached_prefix,
        )
    except Exception as exc:  # never propagate into the workflow
        logger.warning("LLM generation failed (%s) — falling back to deterministic output", exc)
        return None


def generate_json(system: str, user: str, **kwargs) -> dict | None:
    """Like :func:`generate` but parse the reply as JSON; None on any failure.

    Tolerant of ```json code fences and surrounding prose — extracts the first
    balanced object. Returns None (→ deterministic fallback) if parsing fails.
    """

    text = generate(system, user, **kwargs)
    if not text:
        return None
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    raw = fenced.group(1) if fenced else text
    try:
        return json.loads(raw)
    except Exception:
        try:
            start, end = raw.find("{"), raw.rfind("}")
            if start >= 0 and end > start:
                return json.loads(raw[start:end + 1])
        except Exception:
            pass
    logger.warning("LLM JSON parse failed — falling back to deterministic output")
    return None
