from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import stripe
from app.db import get_session

from app.db import SessionDep
from app.schemas.subscription import SubscriptionIn, SubscriptionOut
from app.services.subscription import SubscriptionService

router = APIRouter(tags=["Subscriptions"], prefix="/subscriptions")

stripe.api_key = "sk_test_51QYvHtFsQfGGW0ICxy4d4fUd7wy8gYzrdf2KMBGQrIaltvoB81bys1rkgL3ZpYs5g3SUqipUg4zmYe6Q7JA6DkIM00hGhIn3ED"


@router.post("/create", status_code=200)
async def create_subscription(
    subscription_data: SubscriptionIn,
    session: AsyncSession = Depends(get_session),
):
    try:
        # Создаем сессию Stripe Checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": subscription_data.plan_id,  # ID плана подписки Stripe
                    "quantity": 1,
                },
            ],
            metadata={"user_id": subscription_data.user_id},  # Дополнительные данные
            success_url="http://localhost:8501/",
            cancel_url="https://localhost:8501/",
            expand=["line_items"],
        )

        # Возвращаем ссылку на Checkout
        return {"checkout_url": checkout_session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка Stripe: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Произошла ошибка: {str(e)}",
        )


@router.get("/{subscription_id}", response_model=SubscriptionOut)
async def get_subscription_by_id(
    subscription_id: int,
    session: SessionDep,
):
    return await SubscriptionService.get_subscription_by_id(subscription_id, session)


@router.get("/user/{user_id}", response_model=list[SubscriptionOut])
async def get_user_subscriptions(
    user_id: int,
    session: SessionDep,
):
    try:
        return await SubscriptionService.get_user_subscriptions(user_id, session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Произошла ошибка: {str(e)}",
        )


@router.delete("/{subscription_id}", status_code=200)
async def delete_subscription_by_id(
    subscription_id: int,
    session: SessionDep,
):
    try:
        return await SubscriptionService.delete_subscription_by_id(subscription_id, session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Произошла ошибка: {str(e)}",
        )