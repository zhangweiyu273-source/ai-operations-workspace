from app.ai.prompts.operation_analysis import SYSTEM_PROMPT as BASE_SYSTEM_PROMPT, build_prompt

PROMPT_VERSION = "v1"
SYSTEM_PROMPT = BASE_SYSTEM_PROMPT + "本次重点比较内容表现、平台差异、互动和线索；没有对照数据时明确说明。"

__all__ = ["PROMPT_VERSION", "SYSTEM_PROMPT", "build_prompt"]
