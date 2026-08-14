from app.ai.prompts.operation_analysis import SYSTEM_PROMPT as BASE_SYSTEM_PROMPT, build_prompt

PROMPT_VERSION = "v1"
SYSTEM_PROMPT = BASE_SYSTEM_PROMPT + "本次重点分析任务完成、执行瓶颈和复盘问题；不要把未记录的问题当作事实。"

__all__ = ["PROMPT_VERSION", "SYSTEM_PROMPT", "build_prompt"]
