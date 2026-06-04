from __future__ import annotations

import pytest

from chinese_rewrite.services.parser import ModelOutputParseError, parse_rewrite_output


def test_parse_rewrite_output_accepts_strict_json() -> None:
    result = parse_rewrite_output(
        '{"concise": "Please confirm payment.", "professional": "Could you please confirm the payment status?"}'
    )

    assert result.concise == "Please confirm payment."
    assert result.professional == "Could you please confirm the payment status?"


def test_parse_rewrite_output_extracts_json_inside_extra_text() -> None:
    result = parse_rewrite_output(
        'Here is the result:\n{"concise":"Done by Friday.","professional":"We will complete the report by Friday."}\nThanks.'
    )

    assert result.concise == "Done by Friday."
    assert result.professional == "We will complete the report by Friday."


def test_parse_rewrite_output_uses_label_fallback() -> None:
    result = parse_rewrite_output(
        "Concise: Please reply today.\nProfessional: Could you please respond by the end of today?"
    )

    assert result.concise == "Please reply today."
    assert result.professional == "Could you please respond by the end of today?"


def test_parse_rewrite_output_rejects_missing_professional() -> None:
    with pytest.raises(ModelOutputParseError) as exc:
        parse_rewrite_output('{"concise": "Please reply today."}')

    assert str(exc.value) == "Model output did not contain both rewrite fields."


def test_parse_rewrite_output_rejects_empty_fields() -> None:
    with pytest.raises(ModelOutputParseError):
        parse_rewrite_output('{"concise": " ", "professional": "Polished text."}')
