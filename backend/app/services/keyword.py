import csv
import logging
import re
import unicodedata
from io import StringIO
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import Keyword
from app.repositories.keyword import KeywordRepository
from app.schemas.keyword import (
    ImportErrorDetail,
    KeywordCreate,
    KeywordImportPreview,
    KeywordImportResult,
    KeywordListResponse,
    KeywordResponse,
    KeywordStatistics,
    KeywordUpdate,
)
from app.services.keyword_import import REQUIRED_HEADERS, normalize_keyword_row, parse_keyword_file

logger = logging.getLogger(__name__)


def normalize_keyword(value: str) -> str:
    """Normalize only presentation differences; preserve semantic Chinese content."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value).strip()).casefold()


class KeywordService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = KeywordRepository(session)

    def _build(
        self,
        organization_id: UUID,
        data: KeywordCreate | KeywordUpdate,
        existing: Keyword | None = None,
    ) -> Keyword:
        values = data.model_dump()
        normalized = normalize_keyword(values["keyword"])
        if self.repository.duplicate_exists(
            organization_id, normalized, existing.id if existing else None
        ):
            raise AppError(
                "该组织中已存在规范化后的相同关键词", status_code=409, code="KEYWORD_DUPLICATE"
            )
        if existing is None:
            return Keyword(organization_id=organization_id, normalized_keyword=normalized, **values)
        for field, value in values.items():
            setattr(existing, field, value)
        existing.normalized_keyword = normalized
        return existing

    def list_keywords(self, organization_id: UUID, **params) -> KeywordListResponse:
        items, total = self.repository.list(organization_id, **params)
        return KeywordListResponse.create(
            items=[KeywordResponse.model_validate(item) for item in items],
            total=total,
            page=params["page"],
            page_size=params["page_size"],
        )

    def get(self, organization_id: UUID, keyword_id: UUID) -> Keyword:
        item = self.repository.get(organization_id, keyword_id)
        if item is None:
            raise AppError("关键词不存在", status_code=404, code="KEYWORD_NOT_FOUND")
        return item

    def create(self, organization_id: UUID, data: KeywordCreate) -> KeywordResponse:
        item = self._build(organization_id, data)
        try:
            self.repository.add(item)
            self.session.commit()
            self.session.refresh(item)
        except Exception:
            self.session.rollback()
            logger.exception("Keyword create failed organization_id=%s", organization_id)
            raise
        return KeywordResponse.model_validate(item)

    def update(
        self, organization_id: UUID, keyword_id: UUID, data: KeywordUpdate
    ) -> KeywordResponse:
        item = self._build(organization_id, data, self.get(organization_id, keyword_id))
        try:
            self.session.commit()
            self.session.refresh(item)
        except Exception:
            self.session.rollback()
            logger.exception(
                "Keyword update failed organization_id=%s keyword_id=%s",
                organization_id,
                keyword_id,
            )
            raise
        return KeywordResponse.model_validate(item)

    def delete(self, organization_id: UUID, keyword_id: UUID) -> None:
        item = self.get(organization_id, keyword_id)
        try:
            item.is_deleted = True
            self.session.commit()
        except Exception:
            self.session.rollback()
            logger.exception(
                "Keyword delete failed organization_id=%s keyword_id=%s",
                organization_id,
                keyword_id,
            )
            raise

    def statistics(self, organization_id: UUID, **params) -> KeywordStatistics:
        values = self.repository.statistics(organization_id, **params)
        return KeywordStatistics(
            total=values[0],
            high_commercial_intent=values[1],
            unused=values[2],
            in_topics=values[3],
            platform_count=values[4],
            subject_count=values[5],
        )

    def import_file(
        self, organization_id: UUID, filename: str, content: bytes, confirm: bool
    ) -> KeywordImportResult:
        try:
            headers, rows = parse_keyword_file(filename, content)
        except ValueError as exc:
            raise AppError(str(exc), status_code=400, code="KEYWORD_IMPORT_FILE_INVALID") from exc
        missing = REQUIRED_HEADERS - set(headers)
        if missing:
            raise AppError(
                f"缺少必填列：{', '.join(sorted(missing))}",
                status_code=400,
                code="KEYWORD_IMPORT_HEADERS_INVALID",
            )
        valid, batch_keys, errors, duplicates = [], set(), [], 0
        for row_number, row in enumerate(rows, start=2):
            try:
                payload = KeywordCreate.model_validate(normalize_keyword_row(row))
                key = normalize_keyword(payload.keyword)
                if key in batch_keys or self.repository.duplicate_exists(organization_id, key):
                    duplicates += 1
                    continue
                batch_keys.add(key)
                valid.append((row_number, payload))
            except (ValueError, ValidationError) as exc:
                errors.append(ImportErrorDetail(row=row_number, field="row", message=str(exc)))
        success = 0
        if confirm and not errors:
            try:
                for _, payload in valid:
                    self.repository.add(self._build(organization_id, payload))
                self.session.commit()
                success = len(valid)
            except Exception:
                self.session.rollback()
                logger.exception(
                    "Keyword import failed organization_id=%s filename=%s rows=%s",
                    organization_id,
                    filename,
                    len(valid),
                )
                raise
        return KeywordImportResult(
            total_rows=len(rows),
            success_count=success,
            failed_count=len(errors),
            duplicate_count=duplicates,
            errors=errors[:100],
            preview=[
                KeywordImportPreview(row=n, keyword=p.keyword, platform=p.platform, source=p.source)
                for n, p in valid[:20]
            ],
            can_import=not errors,
        )

    def export_csv(self, organization_id: UUID, **params) -> str:
        rows, _ = self.repository.list(
            organization_id,
            page=1,
            page_size=100000,
            sort_by="updated_at",
            sort_order="desc",
            **params,
        )
        output = StringIO()
        output.write("\ufeff")
        writer = csv.writer(output)
        headers = [
            "关键词",
            "平台",
            "来源",
            "城市",
            "学段",
            "年级",
            "学科",
            "需求类型",
            "痛点",
            "搜索意图",
            "商业意图",
            "内容状态",
            "状态",
            "备注",
        ]
        writer.writerow(headers)
        for item in rows:
            writer.writerow(
                [
                    item.keyword,
                    item.platform or "",
                    item.source or "",
                    item.city or "",
                    item.school_stage or "",
                    item.grade or "",
                    item.subject or "",
                    item.need_type or "",
                    item.pain_point or "",
                    item.search_intent or "",
                    item.commercial_intent or "",
                    item.content_status or "",
                    item.status,
                    item.notes or "",
                ]
            )
        return output.getvalue()
