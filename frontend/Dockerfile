# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем необходимые системные пакеты
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт для Streamlit
EXPOSE 8501

# Команда для запуска приложения
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]