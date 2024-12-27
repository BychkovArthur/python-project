import pandas as pd
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.daos.session import SessionDao
from app.schemas.sessions import SessionSchema
from app.models.user import User as UserModel
from io import StringIO
import csv
from loguru import logger

from app.services.ml import preproc_pred

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

        # Загружаем CSV как DataFrame
        f = StringIO(file)
        df = pd.read_csv(f)

        # Сохраняем исходный CSV, чтобы позже добавить к нему предсказания
        original_df = df.copy()

        # Убираем столбец session_owner, если он существует
        if 'session_owner' in df.columns:
            df = df.drop(columns=['session_owner'])

        # Применяем функцию preproc_pred для получения вероятностей для всех сессий
        # Здесь передаем весь обрезанный CSV (df), а не отдельные строки
        predictions = [prediction[1] for prediction in preproc_pred(df)]  # Вероятности для всех строк

        # Добавляем предсказания (вероятность класса 0) в исходный DataFrame
        original_df['prediction'] = predictions  # Сохраняем только для класса 0

        # Преобразуем обновленный DataFrame в строку CSV
        output = StringIO()
        original_df.to_csv(output, index=False)
        modified_csv = output.getvalue()

        # Перебираем строки исходного DataFrame и сохраняем данные с предсказанием в БД
        session_dao = SessionDao(session)

        for idx, row in original_df.iterrows():
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

            # Получаем предсказание для текущей строки
            prediction = row['prediction']

            session_data = {
                "user_id": current_user.id,
                "payload": payload,
                "prediction": prediction,  # Используем предсказание для класса 0,
                "session_owner": row["session_owner"],
            }

            try:
                # Сохраняем сессию в БД
                await session_dao.create(session_data)
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Error creating session"
                )

        return JSONResponse(
            content={"message": "Sessions created successfully.", "csv": modified_csv},
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
            print(result)
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
