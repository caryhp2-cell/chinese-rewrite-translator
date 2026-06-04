from __future__ import annotations

import json
import re
from typing import Any

from chinese_rewrite.core.models import RewriteResult


class ModelOutputParseError(ValueError):
    pass


def parse_rewrite_output(raw_output: str) -> RewriteResult:
    for candidate in _json_candidates(raw_output):
        parsed = _parse_json_candidate(candidate)
        if parsed is not None:
            return parsed

    fallback = _parse_label_fallback(raw_output)
    if fallback is not None:
        return fallback

    raise ModelOutputParseError("Model output did not contain both rewrite fields.")


def _json_candidates(raw_output: str) -> list[str]:
    stripped = raw_output.strip()
    candidates = [stripped]

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(stripped[start : end + 1])

    return candidates


def _parse_json_candidate(candidate: str) -> RewriteResult | None:
    try:
        payload: Any = json.loads(candidate)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    concise = payload.get("concise")
    professional = payload.get("professional")
    if not isinstance(concise, str) or not isinstance(professional, str):
        return None

    result = RewriteResult(concise=concise, professional=professional)
    if not result.concise or not result.professional:
        raise ModelOutputParseError("Model output did not contain both rewrite fields.")

    return result


def _parse_label_fallback(raw_output: str) -> RewriteResult | None:
    match = re.search(
        r"Concise:\s*(?P<concise>.+?)\s*Professional:\s*(?P<professional>.+)\s*$",
        raw_output,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None

    result = RewriteResult(
        concise=match.group("concise"),
        professional=match.group("professional"),
    )
    if not result.concise or not result.professional:
        return None

    return result
