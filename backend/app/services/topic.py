import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import Keyword, Topic, TopicKeyword
from app.repositories.topic import TopicRepository
from app.schemas.topic import (
    TopicCreate,
    TopicKeywordResponse,
    TopicListResponse,
    TopicResponse,
    TopicStats,
    TopicUpdate,
)

logger = logging.getLogger(__name__)


class TopicService:
    def __init__(self, s: Session):
        self.session = s
        self.repo = TopicRepository(s)

    def response(self, item: Topic):
        account = self.repo.account(item.organization_id, item.account_id)
        rows = (
            self.session.execute(
                select(Keyword)
                .join(TopicKeyword, TopicKeyword.keyword_id == Keyword.id)
                .where(TopicKeyword.topic_id == item.id, Keyword.is_deleted.is_(False))
            )
            .scalars()
            .all()
        )
        data = {
            **item.__dict__,
            "account_name": account.account_name if account else "已删除账号",
            "keyword_count": len(rows),
            "keywords": [
                TopicKeywordResponse(id=k.id, keyword=k.keyword, platform=k.platform) for k in rows
            ],
            "keyword_ids": [k.id for k in rows],
        }
        return TopicResponse.model_validate(data)

    def build(self, org: UUID, data: TopicCreate | TopicUpdate, item: Topic | None = None):
        account = self.repo.account(org, data.account_id)
        if not account:
            raise AppError("关联账号不存在或已删除", 400, "TOPIC_ACCOUNT_NOT_AVAILABLE")
        if account.platform != data.platform:
            raise AppError("选题平台必须与关联账号平台一致", 400, "TOPIC_PLATFORM_ACCOUNT_MISMATCH")
        keywords = self.repo.keywords(org, data.keyword_ids)
        if len(keywords) != len(set(data.keyword_ids)):
            raise AppError("存在不存在或已删除的关键词", 400, "TOPIC_KEYWORD_NOT_AVAILABLE")
        values = data.model_dump(exclude={"keyword_ids"})
        if item is None:
            item = Topic(organization_id=org, **values)
            self.session.add(item)
            self.session.flush()
        else:
            for f, v in values.items():
                setattr(item, f, v)
        self.session.query(TopicKeyword).filter(TopicKeyword.topic_id == item.id).delete(
            synchronize_session=False
        )
        self.session.add_all([TopicKeyword(topic_id=item.id, keyword_id=k.id) for k in keywords])
        return item

    def create(self, org, data):
        try:
            item = self.build(org, data)
            self.session.commit()
            self.session.refresh(item)
        except Exception:
            self.session.rollback()
            logger.exception("Topic create failed organization_id=%s", org)
            raise
        return self.response(item)

    def get(self, org, id):
        item = self.repo.get(org, id)
        if not item:
            raise AppError("选题不存在", 404, "TOPIC_NOT_FOUND")
        return item

    def update(self, org, id, data):
        try:
            item = self.build(org, data, self.get(org, id))
            self.session.commit()
            self.session.refresh(item)
        except Exception:
            self.session.rollback()
            logger.exception("Topic update failed organization_id=%s topic_id=%s", org, id)
            raise
        return self.response(item)

    def delete(self, org, id):
        try:
            self.get(org, id).is_deleted = True
            self.session.commit()
        except Exception:
            self.session.rollback()
            logger.exception("Topic delete failed organization_id=%s topic_id=%s", org, id)
            raise

    def list(self, org, **p):
        items, total = self.repo.list(org, **p)
        return TopicListResponse.create(
            items=[self.response(x) for x in items],
            total=total,
            page=p["page"],
            page_size=p["page_size"],
        )

    def stats(self, org, **p):
        v = self.repo.stats(org, **p)
        return TopicStats(
            total=v[0],
            pending_creation=v[1],
            in_production=v[2],
            published=v[3],
            reviewed=v[4],
            platform_count=v[5],
        )

    def add_keyword(self, org, id, keyword_id):
        try:
            topic = self.get(org, id)
            if not self.repo.keywords(org, [keyword_id]):
                raise AppError("关键词不存在", 404, "TOPIC_KEYWORD_NOT_FOUND")
            if self.session.scalar(
                select(TopicKeyword.id).where(
                    TopicKeyword.topic_id == id, TopicKeyword.keyword_id == keyword_id
                )
            ):
                return self.response(topic)
            self.session.add(TopicKeyword(topic_id=id, keyword_id=keyword_id))
            self.session.commit()
        except Exception:
            self.session.rollback()
            logger.exception("Topic keyword link failed organization_id=%s topic_id=%s", org, id)
            raise
        return self.response(topic)

    def remove_keyword(self, org, id, keyword_id):
        try:
            self.get(org, id)
            link = self.session.scalar(
                select(TopicKeyword).where(
                    TopicKeyword.topic_id == id, TopicKeyword.keyword_id == keyword_id
                )
            )
            if not link:
                raise AppError("关键词关联不存在", 404, "TOPIC_KEYWORD_LINK_NOT_FOUND")
            self.session.delete(link)
            self.session.commit()
        except Exception:
            self.session.rollback()
            logger.exception("Topic keyword unlink failed organization_id=%s topic_id=%s", org, id)
            raise
