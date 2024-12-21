from fastapi import APIRouter, Depends, status, File, UploadFile
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
