from __future__ import annotations


def build_rewrite_prompt(chinese_text: str) -> str:
    cleaned = chinese_text.strip()
    if not cleaned:
        raise ValueError("Chinese input is empty.")

    return (
        "Translate and rewrite the Chinese input into English.\n"
        "Return exactly two versions:\n"
        '1. "concise": brief, natural, clear.\n'
        '2. "professional": polished, business-appropriate, complete.\n'
        "Preserve the original meaning. Do not add facts.\n"
        "Return valid JSON only.\n\n"
        "Expected JSON shape:\n"
        "{\n"
        '  "concise": "Short, clear English version.",\n'
        '  "professional": "Polished professional English version."\n'
        "}\n\n"
        "Chinese input:\n"
        f"{cleaned}"
    )
