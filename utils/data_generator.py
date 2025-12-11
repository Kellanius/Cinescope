import random
import string
from faker import Faker

faker = Faker()

class DataGenerator:

    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    def generate_non_existent_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    def generate_random_name():
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
    def generate_random_password():
        """
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        """
        # Гарантируем наличие хотя бы одной буквы и одной цифры
        letters = random.choice(string.ascii_letters)   # Одна буква
        digits = random.choice(string.digits)   # Одна цифра

        # Дополняем пароль случайными символами из допустимого набора
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)    # Остальная длина пароля
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        # Перемешиваем пароль для рандомизации
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    def generate_negative_random_password_over_max():
        """
        Генерация пароля, не соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 19 до 30 символов.
        """
        # Гарантируем наличие хотя бы одной буквы и одной цифры
        letters = random.choice(string.ascii_letters)  # Одна буква
        digits = random.choice(string.digits)  # Одна цифра

        # Дополняем пароль случайными символами из допустимого набора
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(19, 30)  # Остальная длина пароля
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        # Перемешиваем пароль для рандомизации
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    # Генератор рандомных параметров для фильтра с фильмами
    @staticmethod
    def generate_random_data_for_afisha_filter(correct_data=True, **kwargs):
        """
        :param correct_data: True - данные будут корректными, False - некорректными
        :param kwargs: вручную вносимые данные, которые заменят сгенерированные
        :return: сгенерированные данные для афиша фильтров
        """
        if correct_data is True:
            random_data_for_afisha_filter = {
                "pageSize": random.randint(1, 10),
                "page": 1,
                "minPrice": random.randint(1, 500),
                "maxPrice": random.randint(100, 5000),
                "published": True,
                "genreId": 1,
                "createdAt": "asc"
            }

        # Если correct_data=False, то генерируем maxPrice меньше чем minPrice
        else:
            random_data_for_afisha_filter = {
                "pageSize": random.randint(1, 10),
                "page": 1,
                "minPrice": random.randint(501, 5000),
                "maxPrice": random.randint(1, 500),
                "published": True,
                "genreId": 1,
                "createdAt": "asc"
            }

        random_data_for_afisha_filter.update(kwargs)

        return random_data_for_afisha_filter


    # Генератор рандомного названия и описания для фильма
    @staticmethod
    def generate_random_name_for_movies(max_spaces = 10):
        """
        Генерация названия, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 3 до 60 символов.
        - До 10 рандомных пробелов между символами
        :param max_spaces: максимальное количество пробелов (по умолчанию 10)
        """
        # Гарантируем наличие хотя бы одной буквы и одной цифры
        letters = random.choice(string.ascii_letters)  # Одна буква
        digits = random.choice(string.digits)  # Одна цифра

        # Дополняем название случайными символами из допустимого набора
        special_chars = "?:"
        all_chars = string.ascii_letters + string.digits + special_chars

        # уменьшение remaining_length чтобы учесть пробелы
        remaining_length = random.randint(1, max(1, 58 - max_spaces))  # Остальная длина названия. max - чтобы не было отрицательного значения
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        # Собираем название без пробелов
        movie_name = list(letters + digits + remaining_chars)
        random.shuffle(movie_name)

        # Добавляем пробелы между символами (не в начале и не в конце)
        if len(movie_name) > 1:
            # Определяем, сколько пробелов добавить (от 0 до max_spaces или длины названия минус 1, если оно меньше max_spaces)
            num_spaces = random.randint(0, min(max_spaces, len(movie_name)-1))

            # Выбираем случайные позиции для пробелов (кроме последней позиции)
            space_positions = sorted(random.sample(range(1, len(movie_name)), num_spaces), reverse=True)

            # Вставляем пробелы с конца, чтобы позиции не сдвигались
            for pos in space_positions:
                movie_name.insert(pos, " ")

        # Возвращаем название/описание фильма
        return ''.join(movie_name)


    # Генератор рандомных параметров создания фильма
    @staticmethod
    def generate_random_data_for_new_movies(**kwargs):
        """
        :param kwargs: любые параметры, которые можно вписать вручную для замены рандомно сгенерированных
        :return: сгенерированные данные для фильма
        """

        random_movie_name = DataGenerator.generate_random_name_for_movies()
        random_movie_description = DataGenerator.generate_random_name_for_movies()

        location = ["SPB", "MSK"]

        random_data_for_new_movies = {
            "name": random_movie_name,
            "imageUrl": f"https://image.url",
            "price": random.randint(1, 5000),
            "description": random_movie_description,
            "location": random.choice(location),
            "published": True,
            "genreId": 1
        }

        random_data_for_new_movies.update(kwargs)

        return random_data_for_new_movies


    # Генератор для изменения данных в фильме
    @staticmethod
    def generate_random_data_for_patch_movies_info(movie_data):
        """
        :param movie_data: Данные фильма, которые будем менять
        :return: новые данные фильма
        """
        # Генерируем новые данные на которые будем заменять старые
        new_movie_data_for_patch = DataGenerator.generate_random_data_for_new_movies()

        # Заменяем в новых данных "location" на отличное от текущего "location", чтобы проверить изменение этого параметра
        if movie_data["location"] == "SPB":
            new_movie_data_for_patch["location"] = "MSK"
        else:
            new_movie_data_for_patch["location"] = "SPB"

        return new_movie_data_for_patch


    @staticmethod
    # генератор рандомного id фильма
    def generate_random_id():
        return f"{random.randint(1000000, 2000000)}"





        ##################################################################################################
        # Оказалось что imageUrl это url изображения (шок), а не url фильма, поэтому данный генератор не нужен
        """# Генератор рандомного URL для фильма
        @staticmethod
        def generate_url_for_movies(movie_name):
            """
        # Генерация url. Принимает имя фильма и делает из него url без пробелов и спец символов
        #:param movie_name: имя фильма
        """
            # Проверка всех символов на наличие пробелов и замена их на "_"
            url = movie_name.replace(" ","_")
            url = url.replace("?","")
            url = url.replace(":", "")

            # Возвращаем корректный url фильма
            return url"""
    ##################################################################################################