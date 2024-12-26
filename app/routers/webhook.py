from fastapi import APIRouter, Request, HTTPException, status, Depends
from stripe import Webhook, WebhookSignature
from app.services.subscription import SubscriptionService
from app.services.user import UserService
from sqlalchemy.ext.asyncio import AsyncSession
import stripe
from app.db import get_session

router = APIRouter(tags=["Stripe Webhooks"], prefix="/webhook")

STRIPE_SECRET_KEY = "sk_test_51QYvHtFsQfGGW0ICxy4d4fUd7wy8gYzrdf2KMBGQrIaltvoB81bys1rkgL3ZpYs5g3SUqipUg4zmYe6Q7JA6DkIM00hGhIn3ED"

@router.post("/")
async def stripe_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = "whsec_08b16be03fc90b7a68dfd449b2128395c79fccd8808df47b8d6a903d26e46f16"

    try:
        # Проверяем подпись вебхука
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # Обработка событий Stripe
    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]

        # Запрашиваем дополнительные данные, включая line_items
        checkout_session = stripe.checkout.Session.retrieve(
            session_data["id"],
            expand=["line_items"]
        )

        # Проверяем наличие line_items
        if "line_items" in checkout_session and checkout_session["line_items"]["data"]:
            price_id = checkout_session["line_items"]["data"][0]["price"]["id"]
            user_id = int(checkout_session["metadata"]["user_id"])

            # Создаем запись о подписке
            await SubscriptionService.handle_successful_payment(user_id, price_id, session)
            await UserService.update_user_role(user_id, "premium", session)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Line items not found in session data"
            )

    return {"message": "Webhook received"}