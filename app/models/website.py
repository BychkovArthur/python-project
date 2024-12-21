from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, intpk


class Website(Base):
    __tablename__ = "websites"

    id: Mapped[intpk]
    url: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
