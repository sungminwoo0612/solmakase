"""
커스텀 타입 정의 (UUID 호환 GUID)

PostgreSQL에서는 고유 UUID 타입을 사용하고,
SQLite 등 기타 DB에서는 문자열(CHAR(36))로 UUID를 저장하기 위한 타입입니다.
"""
from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    """
    플랫폼 독립적인 GUID/UUID 타입

    - PostgreSQL: UUID(as_uuid=True)
    - 기타 DB: CHAR(36) 문자열로 저장
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value: Any, dialect) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        # 이미 문자열인 경우도 UUID로 한 번 검증
        return str(uuid.UUID(str(value)))

    def process_result_value(self, value: Any, dialect) -> Optional[uuid.UUID]:
        if value is None:
            return None
        # DB에서 int 등을 돌려줘도 문자열로 한 번 감싸서 UUID 생성 시도
        return uuid.UUID(str(value))


