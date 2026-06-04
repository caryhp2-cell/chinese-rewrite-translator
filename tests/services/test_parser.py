from __future__ import annotations

import pytest

from chinese_rewrite.services.prompts import build_rewrite_prompt
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


def test_parse_rewrite_output_skips_prompt_example_json() -> None:
    raw_output = (
        build_rewrite_prompt("請確認付款狀態。")
        + '\n\nAnswer:\n{"concise":"Please confirm payment.","professional":"Could you please confirm the payment status?"}'
    )

    result = parse_rewrite_output(raw_output)

    assert result.concise == "Please confirm payment."
    assert result.professional == "Could you please confirm the payment status?"


def test_parse_rewrite_output_uses_label_fallback() -> None:
    result = parse_rewrite_output(
        "Concise: Please reply today.\nProfessional: Could you please respond by the end of today?"
    )

    assert result.concise == "Please reply today."
    assert result.professional == "Could you please respond by the end of today?"


@pytest.mark.parametrize(
    "raw_output",
    [
        (
            "Use this schema:\n"
            "concise: brief version\n"
            "professional: polished version"
        ),
        (
            'Use these labels:\n'
            '"Concise: brief version"\n'
            '"Professional: polished version"'
        ),
    ],
)
def test_parse_rewrite_output_rejects_echoed_prompt_labels(raw_output: str) -> None:
    with pytest.raises(ModelOutputParseError):
        parse_rewrite_output(raw_output)


def test_parse_rewrite_output_accepts_clear_line_start_labels() -> None:
    result = parse_rewrite_output("Concise: A short reply.\nProfessional: A polished reply.")

    assert result.concise == "A short reply."
    assert result.professional == "A polished reply."


def test_parse_rewrite_output_rejects_missing_professional() -> None:
    with pytest.raises(ModelOutputParseError) as exc:
        parse_rewrite_output('{"concise": "Please reply today."}')

    assert str(exc.value) == "Model output did not contain both rewrite fields."


def test_parse_rewrite_output_rejects_empty_fields() -> None:
    with pytest.raises(ModelOutputParseError):
        parse_rewrite_output('{"concise": " ", "professional": "Polished text."}')


@pytest.mark.parametrize(
    "raw_output",
    [
        "Concise: \nProfessional: Polished text.",
        "Concise: Polished text.\nProfessional: ",
    ],
)
def test_parse_rewrite_output_rejects_empty_label_fields(raw_output: str) -> None:
    with pytest.raises(ModelOutputParseError):
        parse_rewrite_output(raw_output)


def test_parse_rewrite_output_finds_json_between_brace_noise() -> None:
    result = parse_rewrite_output(
        'debug {not json} {"concise":"A","professional":"B"} trailing {noise}'
    )

    assert result.concise == "A"
    assert result.professional == "B"


@pytest.mark.parametrize(
    "raw_output",
    [
        '{"concise": null, "professional": null} {"concise":"A","professional":"B"}',
        '{"concise": "", "professional": ""} {"concise":"A","professional":"B"}',
    ],
)
def test_parse_rewrite_output_skips_bad_json_candidate_before_good_json(
    raw_output: str,
) -> None:
    result = parse_rewrite_output(raw_output)

    assert result.concise == "A"
    assert result.professional == "B"


@pytest.mark.parametrize(
    "raw_output",
    [
        '{"concise": 1, "professional": "Polished text."}',
        '{"concise": "Brief text.", "professional": ["Polished text."]}',
    ],
)
def test_parse_rewrite_output_rejects_non_string_json_fields(raw_output: str) -> None:
    with pytest.raises(ModelOutputParseError):
        parse_rewrite_output(raw_output)
