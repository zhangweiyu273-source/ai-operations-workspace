from app.ai.prompts.operation_analysis import SYSTEM_PROMPT as BASE_SYSTEM_PROMPT, build_prompt

PROMPT_VERSION = "v1"
SYSTEM_PROMPT = BASE_SYSTEM_PROMPT + "本次重点分析高商业意图、未使用关键词和内容覆盖缺口；不要捏造搜索量。"

__all__ = ["PROMPT_VERSION", "SYSTEM_PROMPT", "build_prompt"]
