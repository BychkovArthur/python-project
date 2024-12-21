from sqlalchemy import JSON, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, intpk


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)  # array of {website_id, visited_ts}
    prediction: Mapped[float] = mapped_column(Float, nullable=False)  # Probability of bad session

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
