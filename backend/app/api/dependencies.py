from typing import Annotated
from uuid import UUID

from fastapi import Header

from app.core.config import get_settings


def get_current_organization_id(
    organization_id: Annotated[UUID | None, Header(alias="X-Organization-ID")] = None,
) -> UUID:
    """Resolve tenant context, falling back to the configured V1 organization."""

    return organization_id or get_settings().default_organization_id
