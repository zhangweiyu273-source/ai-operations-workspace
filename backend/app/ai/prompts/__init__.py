from app.ai.prompts.operation_analysis import PROMPT_VERSION
from app.ai.prompts import content_analysis, keyword_analysis, operation_analysis, task_review_analysis, topic_analysis

PROMPTS = {"operation": operation_analysis, "content": content_analysis, "keyword": keyword_analysis, "topic": topic_analysis, "task_review": task_review_analysis}

def get_prompt(analysis_type: str) -> tuple[str, str]:
    prompt = PROMPTS[analysis_type]
    return prompt.SYSTEM_PROMPT, prompt.PROMPT_VERSION

__all__ = ["PROMPT_VERSION", "get_prompt"]
