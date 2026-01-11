from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_requester.sql_alchemy_client_simple_example import password
from resources.db_creds import MoviesDbCreds
import psycopg2


USERNAME = MoviesDbCreds.USERNAME
PASSWORD = MoviesDbCreds.PASSWORD
HOST = MoviesDbCreds.HOST
PORT = MoviesDbCreds.PORT
DATABASE_NAME = MoviesDbCreds.DATABASE_NAME


# движок для подключения к базе данных
engine = create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}",
    echo=False) # Установить True для отладки SQL запросов

# создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Удобный способ получить новую сессию
def get_db_session():
    """Создаёт новую сессию БД"""
    return SessionLocal()


# подключается к БД мувиес, с выводом информации о PostgreSQL сервере
def connect_to_postgres_movies():
    """Функция для подключения к PostgreSQL базе данных Movies"""
    try:
        connection = psycopg2.connect(
            dbname = DATABASE_NAME,
            user = USERNAME,
            password = PASSWORD,
            host = HOST,
            port = PORT
        )

        print("Подключение успешно установлено")

        # Создание курсора
        cursor = connection.cursor()

        # Вывод информации о PostgreSQL сервере
        print("Информация о сервере PostgreSQL:")
        print(connection.get_dsn_parameters(), "\n")

        # Выполнение SQL-запроса
        cursor.execute("SELECT version();")

        # Получение результата
        record = cursor.fetchone()
        print("Вы подключены к - ", record, "\n")

    except Exception as error:
        print("Ошибка при работе с PostgreSQL:", error)


    finally:
        # Закрытие соединения с базой данных
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Соединение с PostgreSQL закрыто")

if __name__ == "__main__":
        connect_to_postgres_movies()