from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.daos.session import SessionDao
from app.models.user import User as UserModel
from io import StringIO
import csv
import random
from loguru import logger

class SessionService:
    @staticmethod
    async def create(file: str, current_user: UserModel, session: AsyncSession):
        """
        Создает новые сессии на основе данных из CSV-файла.

        :param file: содержимое CSV-файла как строка
        :param current_user: текущий авторизованный пользователь (из которого получаем user_id)
        :param session: сессия базы данных
        :return: список созданных сессий
        """

        f = StringIO(file)
        reader = csv.DictReader(f, delimiter=',')
        session_dao = SessionDao(session)

        for row in reader:
            payload = []

            for i in range(1, 11):  # Для каждого siteX и timeX
                site_key = f"site{i}"
                time_key = f"time{i}"
                
                site_value = row.get(site_key)
                time_value = row.get(time_key)
                
                if site_value and time_value:
                    payload.append({
                        "site": site_value,
                        "time": time_value
                    })
            
            prediction = random.random()
            session_data = {
                "user_id": current_user.id,
                "payload": payload,
                "prediction": prediction
            }
            created_session = await session_dao.create(session_data)

        return JSONResponse(
            content={"message": f"sessions created successfully."},
            status_code=status.HTTP_201_CREATED
        )
