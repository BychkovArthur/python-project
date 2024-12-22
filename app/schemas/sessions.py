from pydantic import BaseModel, ConfigDict, field_serializer
from typing import List, Optional
from datetime import datetime


class SessionSchema(BaseModel):
    id: int
    user_id: int
    payload: List[dict]
    prediction: float
    session_owner: Optional[str]
    created_ts: datetime  # Изменено на datetime

    # Добавляем сериализатор для преобразования created_ts в строку
    @field_serializer("created_ts")
    def serialize_created_ts(self, value: datetime) -> str:
        return value.isoformat()  # Преобразуем datetime в ISO-8601 формат

    # Новая конфигурация для использования from_orm
    model_config = ConfigDict(from_attributes=True)
