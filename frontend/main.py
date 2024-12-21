import streamlit as st
import requests
from streamlit_cookies_controller import CookieController

API_URL = "http://localhost:8000/api/v1"

# Инициализируем контроллер куков
controller = CookieController()

# Функция для отправки POST-запроса для регистрации пользователя
def register_user():
    st.title("Регистрация пользователя")

    email = st.text_input("Email")
    password = st.text_input("Пароль", type="password")

    if st.button("Зарегистрироваться"):
        user_data = {
            "email": email,
            "password": password,
            "role": "partner"  # Устанавливаем роль как 'partner'
        }
        response = requests.post(f"{API_URL}/user/register", json=user_data)
        if response.status_code == 201:
            st.success("Пользователь успешно зарегистрирован!")
        else:
            st.error(f"Ошибка регистрации: {response.text}")

# Функция для получения токена
def get_token():
    st.title("Вход")

    username = st.text_input("Email")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти"):
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{API_URL}/user/token", data=data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            st.success(f"Вы успешно авторизованы")

            # Сохраняем токен в куки
            controller.set("jwt_token", token)
            st.session_state.token = token
        else:
            st.error(f"Ошибка получения токена: {response.text}")

# Функция для проверки авторизации
def check_authorization(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/user/login", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Функция для выхода (удаление токена)
def logout():
    controller.remove("jwt_token")
    st.session_state.token = None
    st.success("Вы успешно вышли из аккаунта!")
    st.rerun()

# Профиль пользователя
def profile_page():
    token = controller.get("jwt_token")
    if token:
        user_data = check_authorization(token)
        if user_data:
            st.title("Профиль")
            st.write(f"Email: {user_data['email']}")
            st.write(f"Роль: {user_data['role']}")
            if st.button("Выход"):
                logout()
        else:
            st.error("Невалидный токен. Пожалуйста, войдите снова.")
    else:
        st.error("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")

# Функция для загрузки CSV файла и создания сессий
def upload_csv_file():
    token = controller.get("jwt_token")
    if token:
        st.title("Загрузка CSV файла")

        # Загружаем файл через Streamlit
        csv_file = st.file_uploader("Выберите CSV файл", type=["csv"])

        if csv_file:
            # Отправляем CSV файл на сервер
            headers = {"Authorization": f"Bearer {token}"}
            files = {"file": csv_file.getvalue()}

            response = requests.post(f'{API_URL}/session/upload_csv', headers=headers, files=files)

            if response.status_code == 201:
                st.success("Сессии успешно созданы!")
            else:
                st.error(f"Ошибка при загрузке файла: {response.text}")
    else:
        st.error("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")

# Основная навигация в приложении
def main():
    st.sidebar.title("Навигация")
    selection = st.sidebar.radio(
        "Выберите действие",
        ["Регистрация", "Вход", "Профиль", "Загрузка CSV"]
    )

    if selection == "Регистрация":
        register_user()
    elif selection == "Вход":
        get_token()
    elif selection == "Профиль":
        profile_page()
    elif selection == "Загрузка CSV":
        upload_csv_file()

if __name__ == "__main__":
    main()
