import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re


def parse_kinopoisk_user_ratings(user_id):
    """
    Парсит оценки пользователя Кинопоиска

    Args:
        user_id (str): ID пользователя на Кинопоиске

    Returns:
        list: Список словарей с информацией о фильмах и оценках
    """
    base_url = f"https://www.kinopoisk.ru/user/{user_id}/votes/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.kinopoisk.ru/"
    }

    data = []
    page_num = 1

    while True:
        if page_num == 1:
            url = base_url
        else:
            url = f"{base_url}list/ord/date/page/{page_num}/"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Проверяем, не перенаправляет ли нас на капчу
            if "captcha" in response.url:
                print("Обнаружена капча. Прерывание парсинга.")
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем контейнер с фильмами
            films_container = soup.find('div', class_='profileFilmsList')
            if not films_container:
                print("Не удалось найти контейнер с фильмами.")
                break

            # Ищем все элементы с фильмами
            film_items = films_container.find_all('div', class_='item')
            if not film_items:
                print(f"На странице {page_num} не найдено фильмов. Завершение.")
                break

            print(f"Обрабатывается страница {page_num}, найдено {len(film_items)} фильмов")

            for item in film_items:
                try:
                    # Извлекаем название фильма
                    name_elem = item.find('div', class_='nameRus')
                    if name_elem:
                        film_name = name_elem.find('a').get_text(strip=True)
                    else:
                        name_elem = item.find('div', class_='nameEng')
                        film_name = name_elem.find('a').get_text(strip=True) if name_elem else "Неизвестно"

                    # Извлекаем количество оценок фильма
                    number_elem = item.find('div', class_='rating')
                    number = number_elem.find('span').get_text(strip=True) if number_elem else "Неизвестно"

                    # Извлекаем оценку
                    rating_elem = item.find('div', class_='vote')
                    rating = rating_elem.get_text(strip=True) if rating_elem else "Без оценки"

                    # Извлекаем среднюю оценку пользователей
                    average_rating_elem = item.find('div', class_='rating')
                    average_rating = average_rating_elem.find('b').get_text(strip=True) if average_rating_elem else "Без оценки"

                    # Добавляем данные
                    data.append({
                        'Film name and year': film_name,
                        'Number of ratings': number,
                        'User rating': rating,
                        'Average rating': average_rating
                    })

                except Exception as e:
                    print(f"Ошибка при обработке элемента: {e}")
                    continue

            # Проверяем наличие следующей страницы
            next_page = soup.find('a', class_='arrow', string='»')
            if not next_page:
                break

            page_num += 1
            time.sleep(1)  # Задержка между запросами

        except requests.RequestException as e:
            print(f"Ошибка при запросе страницы {page_num}: {e}")
            break

    return data


def export_to_csv(data, filename):
    """
    Экспортирует данные в CSV файл

    Args:
        data (list): Данные для экспорта
        filename (str): Имя файла для сохранения
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"Данные сохранены в {filename}")


def export_to_excel(data, filename):
    """
    Экспортирует данные в Excel файл

    Args:
        data (list): Данные для экспорта
        filename (str): Имя файла для сохранения
    """
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Данные сохранены в {filename}")


if __name__ == "__main__":
    # Пример использования
    user_id = "ваш_id_пользователя"  # !!Замените на реальный ID пользователя!!

    print("Начинаем парсинг оценок пользователя Кинопоиска...")
    data = parse_kinopoisk_user_ratings(user_id)

    if data:
        print(f"Успешно собрано {len(data)} оценок")

        # Экспорт в CSV
        export_to_csv(data, "kinopoisk_ratings.csv")

        # Экспорт в Excel
        export_to_excel(data, "kinopoisk_ratings.xlsx")
    else:
        print("Не удалось собрать данные. Проверьте ID пользователя и доступность страницы.")