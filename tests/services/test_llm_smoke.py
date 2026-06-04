from __future__ import annotations

import os
from pathlib import Path

import pytest

from chinese_rewrite.core.models import AppConfig
from chinese_rewrite.services.llm import LlamaService
from chinese_rewrite.services.prompts import build_rewrite_prompt


@pytest.mark.skipif(
    os.environ.get("RUN_LOCAL_LLM_SMOKE") != "1",
    reason="Set RUN_LOCAL_LLM_SMOKE=1 to run the local GGUF smoke test.",
)
def test_local_llama_runtime_returns_two_rewrite_fields() -> None:
    root = Path.cwd()
    service = LlamaService(root=root, config=AppConfig.default())
    prompt = build_rewrite_prompt("請在週五前回覆我是否可以參加會議。")

    result = service.generate(prompt)

    assert result.concise
    assert result.professional
    assert result.concise != result.professional
