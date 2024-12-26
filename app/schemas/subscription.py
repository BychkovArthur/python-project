from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class SubscriptionBase(BaseModel):
    user_id: int
    plan_id: str 
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SubscriptionIn(SubscriptionBase):
    pass


class SubscriptionOut(SubscriptionBase):
    id: int