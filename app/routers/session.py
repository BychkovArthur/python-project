from fastapi import APIRouter, Depends, status, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.session import SessionService
from app.models.user import User as UserModel
from app.services.user import CurrentUserDep
from app.db import SessionDep

router = APIRouter(tags=["Session"], prefix="/session")

@router.post(
    "/upload_csv",
    status_code=status.HTTP_201_CREATED,
    summary="Create sessions from CSV file",
)
async def create_sessions_from_csv(
    current_user: CurrentUserDep,  # Получаем текущего пользователя
    session: SessionDep,  # Получаем сессию базы данных
    file: UploadFile = File(...),  # Получаем файл через форму
):
    # Читаем файл в строку
    file_content = await file.read()

    # Обрабатываем CSV файл и создаем сессии через сервис
    return await SessionService.create(file_content.decode(), current_user, session)


@router.get(
    "/my_sessions",
    status_code=status.HTTP_200_OK,
    summary="Get sessions for the current user",
)
async def get_sessions_for_current_user(
    current_user: CurrentUserDep,  # Получаем текущего пользователя
    session: SessionDep,  # Получаем сессию базы данных
):
    """
    Возвращает список сессий для текущего пользователя.

    :param current_user: текущий авторизованный пользователь
    :param session: сессия базы данных
    :return: JSON с информацией о сессиях
    """
    # try:
    return await SessionService.get_sessions_by_user(current_user.id, session)
    # except HTTPException as e:
    #     raise e
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="An unexpected error occurred while fetching sessions."
    #     )
