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
    root = Path(__file__).resolve().parents[2]
    base_config = AppConfig.default()
    smoke_config = AppConfig(
        model_relative_path=base_config.model_relative_path,
        runtime_relative_path=base_config.runtime_relative_path,
        temperature=base_config.temperature,
        max_tokens=192,
        timeout_seconds=60,
    )
    service = LlamaService(root=root, config=smoke_config)
    prompt = build_rewrite_prompt("請在週五前回覆我是否可以參加會議。")

    result = service.generate(prompt)

    assert result.concise
    assert result.professional
