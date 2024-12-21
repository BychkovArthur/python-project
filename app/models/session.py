from sqlalchemy import JSON, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.base import Base, intpk


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)  # array of {website_id, visited_ts}
    prediction: Mapped[float] = mapped_column(Float, nullable=False)  # Probability of bad session
    created_ts: Mapped["datetime"] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )  # Timestamp of when the session was created

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
