import csv
import hashlib
import logging
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from io import StringIO
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import OperationMetric
from app.repositories.operation_metric import OperationMetricRepository
from app.schemas.operation_metric import (
    ImportErrorDetail,
    ImportPreviewRow,
    ImportResult,
    MetricStatistics,
    OperationMetricCreate,
    OperationMetricListResponse,
    OperationMetricResponse,
    OperationMetricUpdate,
)
from app.services.metric_import import REQUIRED_HEADERS, normalize_row, parse_tabular_file

logger = logging.getLogger(__name__)


def dedup_key(content_url: str | None, content_title: str) -> str:
    identity = (content_url or content_title).strip().casefold()
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


class OperationMetricService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = OperationMetricRepository(session)

    @staticmethod
    def response(metric: OperationMetric, account_name: str) -> OperationMetricResponse:
        return OperationMetricResponse.model_validate(
            {**metric.__dict__, "account_name": account_name}
        )

    def list_metrics(self, organization_id: UUID, **params) -> OperationMetricListResponse:
        rows, total = self.repository.list(organization_id, **params)
        return OperationMetricListResponse.create(
            items=[self.response(metric, name) for metric, name in rows],
            total=total,
            page=params["page"],
            page_size=params["page_size"],
        )

    def get_metric(self, organization_id: UUID, metric_id: UUID):
        row = self.repository.get(organization_id, metric_id)
        if row is None:
            raise AppError("运营数据不存在", status_code=404, code="OPERATION_METRIC_NOT_FOUND")
        return row

    def _build(
        self,
        organization_id: UUID,
        data: OperationMetricCreate | OperationMetricUpdate,
        existing: OperationMetric | None = None,
    ):
        account = self.repository.account(organization_id, data.account_id)
        if account is None:
            raise AppError(
                "关联账号不存在或已停用删除", status_code=400, code="ACCOUNT_NOT_AVAILABLE"
            )
        key = dedup_key(data.content_url, data.content_title)
        if self.repository.duplicate_exists(
            organization_id,
            data.account_id,
            data.metric_date,
            key,
            existing.id if existing else None,
        ):
            raise AppError(
                "同一账号、日期和内容的数据已存在",
                status_code=409,
                code="OPERATION_METRIC_DUPLICATE",
            )
        values = data.model_dump()
        if existing is None:
            return OperationMetric(
                organization_id=organization_id, platform=account.platform, dedup_key=key, **values
            ), account.account_name
        for field, value in values.items():
            setattr(existing, field, value)
        existing.platform = account.platform
        existing.dedup_key = key
        return existing, account.account_name

    def create(self, organization_id: UUID, data: OperationMetricCreate):
        metric, name = self._build(organization_id, data)
        try:
            self.repository.add(metric)
            self.session.commit()
            self.session.refresh(metric)
        except Exception:
            self.session.rollback()
            logger.exception(
                "Operation metric create failed organization_id=%s account_id=%s",
                organization_id,
                data.account_id,
            )
            raise
        return self.response(metric, name)

    def update(self, organization_id: UUID, metric_id: UUID, data: OperationMetricUpdate):
        metric, _ = self.get_metric(organization_id, metric_id)
        metric, name = self._build(organization_id, data, metric)
        try:
            self.session.commit()
            self.session.refresh(metric)
        except Exception:
            self.session.rollback()
            logger.exception(
                "Operation metric update failed organization_id=%s metric_id=%s",
                organization_id,
                metric_id,
            )
            raise
        return self.response(metric, name)

    def delete(self, organization_id: UUID, metric_id: UUID):
        metric, _ = self.get_metric(organization_id, metric_id)
        try:
            metric.is_deleted = True
            self.session.commit()
        except Exception:
            self.session.rollback()
            logger.exception(
                "Operation metric delete failed organization_id=%s metric_id=%s",
                organization_id,
                metric_id,
            )
            raise

    def statistics(self, organization_id: UUID, **filters) -> MetricStatistics:
        (
            exposure,
            views,
            likes,
            comments,
            favorites,
            shares,
            new_leads,
            valid_leads,
            high_intent,
            trials,
            deals,
            revenue,
        ) = self.repository.statistics(organization_id, **filters)
        interactions = likes + comments + favorites + shares
        rate = lambda numerator, denominator: (
            (Decimal(numerator) / Decimal(denominator) * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            if denominator
            else Decimal("0.00")
        )
        return MetricStatistics(
            exposure=exposure,
            views=views,
            interactions=interactions,
            new_leads=new_leads,
            valid_leads=valid_leads,
            high_intent_leads=high_intent,
            trial_bookings=trials,
            deals=deals,
            revenue=revenue,
            interaction_rate=rate(interactions, views),
            valid_lead_rate=rate(valid_leads, new_leads),
            trial_conversion_rate=rate(trials, valid_leads),
            deal_rate=rate(deals, valid_leads),
        )

    def import_file(
        self, organization_id: UUID, filename: str, content: bytes, confirm: bool
    ) -> ImportResult:
        try:
            headers, rows = parse_tabular_file(filename, content)
        except ValueError as exc:
            raise AppError(str(exc), status_code=400, code="IMPORT_FILE_INVALID") from exc
        missing = REQUIRED_HEADERS - set(headers)
        if missing:
            raise AppError(
                f"缺少必填列：{'、'.join(sorted(missing))}",
                status_code=400,
                code="IMPORT_HEADERS_INVALID",
            )
        accounts = self.repository.accounts_by_name(organization_id)
        errors: list[ImportErrorDetail] = []
        valid: list[tuple[int, OperationMetricCreate, str, str]] = []
        duplicates = 0
        batch_keys: set[tuple[UUID, date, str]] = set()
        for row_number, row in enumerate(rows, start=2):
            try:
                data = normalize_row(row)
                account_name = str(data.pop("account_name") or "")
                matches = accounts.get(account_name, [])
                if not matches:
                    raise ValueError("账号不存在")
                if len(matches) > 1:
                    raise ValueError("账号名称不唯一，请先在账号矩阵中处理")
                account = matches[0]
                payload = OperationMetricCreate(account_id=account.id, **data)
                key = dedup_key(payload.content_url, payload.content_title)
                identity = (account.id, payload.metric_date, key)
                if identity in batch_keys or self.repository.duplicate_exists(
                    organization_id, *identity
                ):
                    duplicates += 1
                    continue
                batch_keys.add(identity)
                valid.append((row_number, payload, account_name, account.platform))
            except (ValueError, ValidationError) as exc:
                errors.append(ImportErrorDetail(row=row_number, field="row", message=str(exc)))
        can_import = not errors
        success = 0
        if confirm and can_import:
            try:
                for _, payload, _, platform in valid:
                    self.repository.add(
                        OperationMetric(
                            organization_id=organization_id,
                            platform=platform,
                            dedup_key=dedup_key(payload.content_url, payload.content_title),
                            **payload.model_dump(),
                        )
                    )
                self.session.commit()
                success = len(valid)
            except Exception:
                self.session.rollback()
                logger.exception(
                    "Operation metric import failed organization_id=%s filename=%s rows=%s",
                    organization_id,
                    filename,
                    len(valid),
                )
                raise
        preview = [
            ImportPreviewRow(
                row=row,
                metric_date=payload.metric_date,
                account_name=name,
                content_title=payload.content_title,
                platform=platform,
            )
            for row, payload, name, platform in valid[:20]
        ]
        return ImportResult(
            total_rows=len(rows),
            success_count=success,
            failed_count=len(errors),
            duplicate_count=duplicates,
            errors=errors[:100],
            preview=preview,
            can_import=can_import,
        )

    def export_csv(self, organization_id: UUID, **filters) -> str:
        rows, _ = self.repository.list(
            organization_id, page=1, page_size=100000, sort_by="date", sort_order="desc", **filters
        )
        output = StringIO()
        output.write("\ufeff")
        writer = csv.writer(output)
        writer.writerow(
            [
                "日期",
                "平台",
                "账号",
                "内容标题",
                "内容链接",
                "内容类型",
                "曝光",
                "播放",
                "点赞",
                "评论",
                "收藏",
                "分享",
                "私信",
                "新增线索",
                "有效线索",
                "高意向",
                "试听",
                "成交",
                "成交金额",
                "备注",
            ]
        )
        for metric, name in rows:
            writer.writerow(
                [
                    metric.metric_date,
                    metric.platform,
                    name,
                    metric.content_title,
                    metric.content_url or "",
                    metric.content_type or "",
                    metric.exposure,
                    metric.views,
                    metric.likes,
                    metric.comments,
                    metric.favorites,
                    metric.shares,
                    metric.private_messages,
                    metric.new_leads,
                    metric.valid_leads,
                    metric.high_intent_leads,
                    metric.trial_bookings,
                    metric.deals,
                    metric.revenue,
                    metric.notes or "",
                ]
            )
        return output.getvalue()
