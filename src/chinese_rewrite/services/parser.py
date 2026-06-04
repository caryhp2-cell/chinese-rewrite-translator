from __future__ import annotations

import json
import re
from typing import Any

from chinese_rewrite.core.models import RewriteResult

_PLACEHOLDER_CONCISE = "Short, clear English version."
_PLACEHOLDER_PROFESSIONAL = "Polished professional English version."
_PARSE_ERROR_MESSAGE = "Model output did not contain both rewrite fields."


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

    raise ModelOutputParseError(_PARSE_ERROR_MESSAGE)


def _json_candidates(raw_output: str) -> list[Any]:
    decoder = json.JSONDecoder()
    candidates: list[Any] = []

    for match in re.finditer(r"{", raw_output):
        try:
            payload, _ = decoder.raw_decode(raw_output, match.start())
        except json.JSONDecodeError:
            continue
        candidates.append(payload)

    return candidates


def _parse_json_candidate(payload: Any) -> RewriteResult | None:
    if not isinstance(payload, dict):
        return None

    if "concise" not in payload or "professional" not in payload:
        return None

    concise = payload.get("concise")
    professional = payload.get("professional")
    if not isinstance(concise, str) or not isinstance(professional, str):
        return None

    result = RewriteResult(concise=concise, professional=professional)
    if not result.concise or not result.professional:
        return None
    if _is_placeholder_result(result):
        return None

    return result


def _is_placeholder_result(result: RewriteResult) -> bool:
    return (
        result.concise == _PLACEHOLDER_CONCISE
        and result.professional == _PLACEHOLDER_PROFESSIONAL
    )


def _parse_label_fallback(raw_output: str) -> RewriteResult | None:
    match = re.search(
        r"\A\s*Concise:[ \t]*(?P<concise>[^\r\n]*)\r?\n"
        r"Professional:[ \t]*(?P<professional>[^\r\n]*)\s*\Z",
        raw_output,
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
