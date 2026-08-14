import json

PROMPT_VERSION = "v1"

SYSTEM_PROMPT = """你是教培行业运营分析助手。仅根据提供的 JSON 事实分析；不知道就写数据不足。不要虚构平台、用户行为或因果关系。严格区分 facts（数据事实）、analysis（解释）、hypotheses（待验证假设）和 recommendations（可执行建议）。只返回 JSON，不使用 Markdown。JSON 必须包含 title, summary, key_findings, positive_signals, risks, possible_causes, recommendations, next_actions, data_limitations, confidence。每个数组项使用简洁中文字符串。"""

def build_prompt(context: dict) -> str:
    return "运营事实数据：\n" + json.dumps(context, ensure_ascii=False, separators=(",", ":"))
