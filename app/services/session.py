from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.daos.session import SessionDao
from app.schemas.sessions import SessionSchema
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
            
            # Извлекаем поле session_owner, если оно существует
            session_owner = row.get("session_owner", None)
            
            prediction = random.random()
            session_data = {
                "user_id": current_user.id,
                "payload": payload,
                "prediction": prediction,
                "session_owner": session_owner  # Добавляем новое поле
            }
            
            try:
                created_session = await session_dao.create(session_data)
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Error creating session"
                )

        return JSONResponse(
            content={"message": "Sessions created successfully."},
            status_code=status.HTTP_201_CREATED
        )

    @staticmethod
    async def get_sessions_by_user(user_id: int, session: AsyncSession):
        """
        Возвращает все сессии для заданного пользователя.

        :param user_id: ID пользователя
        :param session: сессия базы данных
        :return: список сессий
        """
        session_dao = SessionDao(session)
        try:
            sessions = await session_dao.get_by_user_id(user_id)

            # Преобразование объектов SQLAlchemy в JSON-совместимый формат
            result = [SessionSchema.from_orm(session).model_dump() for session in sessions]

            return JSONResponse(
                content=result,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Ошибка получения сессий для пользователя {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка получения сессий"
            )
