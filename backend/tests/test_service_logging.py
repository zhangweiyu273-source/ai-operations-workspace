import logging
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models import Account, OperationMetric
from app.schemas.account import AccountCreate
from app.services.account import AccountService
from app.services.operation_metric import OperationMetricService


def test_account_transaction_failure_rolls_back_and_logs(caplog: pytest.LogCaptureFixture) -> None:
    session = MagicMock()
    session.commit.side_effect = RuntimeError("database write failed")
    service = AccountService(session)
    service.repository.create = MagicMock(
        return_value=Account(
            organization_id=uuid4(),
            platform="小红书",
            account_name="日志测试账号",
            account_type="品牌账号",
        )
    )

    with caplog.at_level(logging.ERROR), pytest.raises(RuntimeError):
        service.create_account(
            uuid4(),
            AccountCreate(
                platform="小红书",
                account_name="日志测试账号",
                account_type="品牌账号",
            ),
        )

    session.rollback.assert_called_once()
    assert "Account create failed" in caplog.text


def test_metric_delete_failure_rolls_back_and_logs(caplog: pytest.LogCaptureFixture) -> None:
    session = MagicMock()
    session.commit.side_effect = RuntimeError("database write failed")
    service = OperationMetricService(session)
    metric = OperationMetric(
        organization_id=uuid4(),
        account_id=uuid4(),
        metric_date="2026-08-14",
        platform="小红书",
        content_title="日志测试内容",
        dedup_key="x" * 64,
    )
    service.get_metric = MagicMock(return_value=(metric, "日志测试账号"))

    with caplog.at_level(logging.ERROR), pytest.raises(RuntimeError):
        service.delete(uuid4(), uuid4())

    session.rollback.assert_called_once()
    assert "Operation metric delete failed" in caplog.text
