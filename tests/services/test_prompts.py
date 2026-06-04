from __future__ import annotations

from chinese_rewrite.services.prompts import build_rewrite_prompt


def test_build_rewrite_prompt_includes_json_contract_and_input() -> None:
    prompt = build_rewrite_prompt("我們需要在週五前完成報告。")

    assert "Return valid JSON only." in prompt
    assert '"concise"' in prompt
    assert '"professional"' in prompt
    assert "Preserve the original meaning. Do not add facts." in prompt
    assert "我們需要在週五前完成報告。" in prompt


def test_build_rewrite_prompt_rejects_empty_input() -> None:
    try:
        build_rewrite_prompt("  \n ")
    except ValueError as exc:
        assert str(exc) == "Chinese input is empty."
    else:
        raise AssertionError("Expected ValueError for empty input")


def test_build_rewrite_prompt_strips_outer_whitespace() -> None:
    prompt = build_rewrite_prompt("  請協助確認付款狀態。  ")

    assert "Chinese input:\n請協助確認付款狀態。" in prompt
