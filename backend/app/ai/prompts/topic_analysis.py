from app.ai.prompts.operation_analysis import SYSTEM_PROMPT as BASE_SYSTEM_PROMPT, build_prompt

PROMPT_VERSION = "v1"
SYSTEM_PROMPT = BASE_SYSTEM_PROMPT + "本次重点分析选题库存、状态、发布覆盖和优先推进方向；重复度不足以判断时必须说明。"

__all__ = ["PROMPT_VERSION", "SYSTEM_PROMPT", "build_prompt"]
