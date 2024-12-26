import streamlit as st
import requests
from streamlit_cookies_controller import CookieController
import stripe
from jwt_parse import UtilsService
from datetime import datetime

API_URL = "http://app:8000/api/v1"

STRIPE_PUBLISHABLE_KEY = "pk_test_51QYvHtFsQfGGW0ICJbQdHSsTU3OFs7lHnUYtvzT3gO0GIVwwBD3MzhCJeWuEGFaUVocBVoVSUWtB0pydoRDikpJE00UspV4tuz"
stripe.api_key = "sk_test_51QYvHtFsQfGGW0ICxy4d4fUd7wy8gYzrdf2KMBGQrIaltvoB81bys1rkgL3ZpYs5g3SUqipUg4zmYe6Q7JA6DkIM00hGhIn3ED"
MONTHLY_PLAN_ID = "price_1QYvQSFsQfGGW0IC3wOIIJOD" 
YEARLY_PLAN_ID = "price_1QYvRJFsQfGGW0ICYmx4P55I" 

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
            st.rerun()
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

def profile_page():
    st.title("Профиль пользователя")
    
    token = controller.get("jwt_token")
    if token:
        credentials = UtilsService.decode_jwt(token)
        user_id = credentials.get("user_id")
        if not user_id:
            st.error("Невалидный токен. Пожалуйста, войдите снова.")
            return
        
        # Получение данных о пользователе
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/user/{user_id}/role", headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            
            with st.container():
                st.write(f"**Email:** {user_data['email']}")

                if user_data['role'] == 'premium':
                    st.markdown(
                        """
                        <span style="color: gold; font-weight: bold; font-size: 18px;">
                            Текущая роль: premium
                        </span>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.write(f"**Роль:** {user_data['role']}")
        else:
            st.error(f"Ошибка загрузки данных: {response.text}")
    else:
        st.error("Вы не авторизованы. Войдите в аккаунт.")

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

# Функция для отображения всех сессий текущего пользователя
def my_sessions():
    token = controller.get("jwt_token")
    if token:
        st.title("Мои сессии")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/session/my_sessions", headers=headers)

        if response.status_code == 200:
            sessions = response.json()
            if not sessions:
                st.info("У вас пока нет сессий.")
            else:
                for session in sessions:
                    prediction = session.get("prediction", 0.0)
                    session_owner = session.get("session_owner", "Не указан")  # Добавляем отображение владельца
                    smilie = "😄" if prediction < 0.3 else "😐" if prediction < 0.7 else "😠"
                    st.write(f"Session ID: {session['id']}")
                    st.write(f"Prediction: {prediction:.2f} {smilie}")
                    st.write(f"Payload: {session['payload']}")
                    st.write(f"Owner: {session_owner}")  # Отображаем владельца
                    st.write("---")
        else:
            st.error(f"Ошибка загрузки сессий: {response.text}")
    else:
        st.error("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")

def payment_page():
    token = controller.get("jwt_token")
    if token:
        st.title("Оплата подписки")

        plan = st.radio("Выберите подписку", ["Месячная", "Годовая"])

        if st.button("Продолжить"):
            try:
                # Определяем ID плана в зависимости от выбранного типа
                plan_id = MONTHLY_PLAN_ID if plan == "Месячная" else YEARLY_PLAN_ID

                # Отправляем запрос на сервер для создания подписки
                headers = {"Authorization": f"Bearer {token}"}
                credantions = UtilsService.decode_jwt(token)

                exp = credantions.get("exp")
                if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                    raise ValueError("Срок действия токена истёк.")
                user_id = int(credantions.get("user_id"))

                payload = {
                    "user_id": user_id,  # Получаем ID пользователя из авторизации
                    "plan_id": plan_id,
                }

                response = requests.post(
                    f"{API_URL}/subscriptions/create",
                    headers=headers,
                    json=payload,
                )

                if response.status_code == 200:
                    checkout_url = response.json().get("checkout_url")
                    if checkout_url:
                        st.markdown(
                            f"""
                            <a href="{checkout_url}" target="_self">
                                <button style="background-color:green;color:white;padding:10px 15px;border:none;border-radius:5px;">
                                    Перейти к оплате
                                </button>
                            </a>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.stop()  # Прерываем выполнение Streamlit
                    else:
                        st.error("Не удалось получить URL для оплаты.")
            except Exception as e:
                st.error(f"Ошибка: {str(e)}")
    else:
        st.error("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")


# История оплат пользователя
def user_subscriptions():
    token = controller.get("jwt_token")
    if token:
        st.title("Мои подписки")

        headers = {"Authorization": f"Bearer {token}"}
        credentials = UtilsService.decode_jwt(token)
        user_id = credentials.get("user_id")  # Получаем ID пользователя из токена

        # Запрос к API для получения подписок
        response = requests.get(f"{API_URL}/subscriptions/user/{user_id}", headers=headers)

        if response.status_code == 200:
            subscriptions = response.json()
            if not subscriptions:
                st.info("У вас пока нет подписок.")
            else:
                # Отображаем подписки в виде таблицы
                st.table([
                    {
                        "ID": sub["id"] + 1,
                        "План": sub["plan_id"],
                        "Дата начала": sub["start_date"],
                        "Дата окончания": sub["end_date"],
                    }
                    for sub in subscriptions
                ])
        else:
            st.error(f"Ошибка загрузки подписок: {response.text}")
    else:
        st.error("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")

def success_page():
    st.title("Оплата успешно завершена!")
    st.write("Спасибо за оплату. Ваша подписка активирована.")

    session_id = st.experimental_get_query_params().get("session_id", [None])[0]
    if session_id:
        st.info("Обновляем роль пользователя...")
        token = controller.get("jwt_token")
        if token:
            credentials = UtilsService.decode_jwt(token)
            user_id = credentials.get("user_id")
            headers = {"Authorization": f"Bearer {token}"}

            # Обновляем роль пользователя
            response = requests.get(f"{API_URL}/user/{user_id}/role", headers=headers)
            if response.status_code == 200:
                st.success("Роль пользователя обновлена.")
            else:
                st.error("Не удалось обновить роль.")

def is_authenticated():
    token = st.session_state.get("token") or controller.get("jwt_token")
    if not token:
        return False
    try:
        # Проверяем срок действия токена
        credantions = UtilsService.decode_jwt(token)
        exp = credantions.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            return False
        return True
    except Exception:
        return False
    
def logout_if_expired():
    if not is_authenticated():
        token = controller.get("jwt_token")  # Проверяем, существует ли кука
        if token:
            controller.remove("jwt_token")
        st.session_state.pop("token", None)

import streamlit.components.v1 as components

def render_logout_button():
    # Проверяем авторизацию
    if is_authenticated():
        # Добавляем HTML-стиль для кнопки
        st.markdown(
            """
            <style>
            .logout-button {
                position: fixed;
                top: 10px;
                right: 10px;
                z-index: 1000;
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                cursor: pointer;
                border-radius: 5px;
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        # Отображение кнопки
        if st.button("Выйти", key="logout_button", help="Нажмите, чтобы выйти"):
            logout()

def main():
    logout_if_expired()
    render_logout_button()
    st.sidebar.title("Навигация")
    
    # Проверяем авторизацию пользователя
    authenticated = is_authenticated()

    # Меню навигации для авторизованных и неавторизованных пользователей
    if authenticated:
        selection = st.sidebar.radio(
            "Выберите действие",
            ["Профиль", "Загрузка CSV", "Мои сессии", "Оплата подписки", "История оплат"]
        )
    else:
        selection = st.sidebar.radio(
            "Выберите действие",
            ["Регистрация", "Вход"]
        )

    # Обработка успешной оплаты
    query_params = st.query_params
    if "success" in query_params:
        success_page()
        return
    elif "cancel" in query_params:
        st.error("Оплата была отменена.")
        return

    # Обработка действий из меню
    if selection == "Регистрация":
        register_user()
    elif selection == "Вход":
        get_token()
    elif selection == "Профиль":
        profile_page()
    elif selection == "Загрузка CSV":
        upload_csv_file()
    elif selection == "Мои сессии":
        my_sessions()
    elif selection == "Оплата подписки":
        payment_page()
    elif selection == "История оплат":
        user_subscriptions()

if __name__ == "__main__":
    main()
