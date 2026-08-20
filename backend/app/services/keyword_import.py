from typing import Any

from app.services.metric_import import parse_tabular_file

REQUIRED_HEADERS = {"关键词"}
FIELD_MAP = {
    "关键词": "keyword",
    "平台": "platform",
    "来源": "source",
    "城市": "city",
    "学段": "school_stage",
    "年级": "grade",
    "学科": "subject",
    "需求类型": "need_type",
    "痛点": "pain_point",
    "搜索意图": "search_intent",
    "商业意图": "commercial_intent",
    "内容状态": "content_status",
    "状态": "status",
    "备注": "notes",
}


def parse_keyword_file(filename: str, content: bytes) -> tuple[list[str], list[dict[str, Any]]]:
    return parse_tabular_file(filename, content)


def normalize_keyword_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        field: (
            str(row.get(header)).strip()
            if row.get(header) is not None and str(row.get(header)).strip()
            else None
        )
        for header, field in FIELD_MAP.items()
    }
    # ``status`` has a Schema default (启用).  Do not override that default
    # with None when an import file omits the optional 状态 column or leaves it blank.
    if normalized["status"] is None:
        normalized.pop("status")
    return normalized
