from sqlalchemy import String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, intpk

class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id: Mapped[str] = mapped_column(String(50), nullable=False)  # 'monthly' или 'yearly'
    start_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    end_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
