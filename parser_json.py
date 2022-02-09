import requests
import json
from bs4 import BeautifulSoup
import random
import time

# Использую заголовки, чтобы сайт сильно не ругался
headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'
}

# Используем прокси, если нужно, и добавляем в get запрос ниже
# если нет логина и пароля,прокси можно добавить в список разрешенных в панели управления 
# proxies = {
#     "https": "your_proxy_ip:port"
#     "http" : ""
# }


def retry(func):
    def wrapper():
        try:
            func()

        except Exception as e:
            print(e)
            time.sleep(30)
            func()

    return wrapper


# функция которая получает все ссылки на сегодняшние новости
def collect_data():
    s = requests.Session()
    # Здесь по коду страницы(//www.zakon.kz/news) прохожу на Network и ищу get запрос, нашел ссылку по которой получаю api json
    # Рассматриваю структуру в online json viewer и меняю Size на 150(отвечает за вывод количества новостей)
    response = s.get(url="https://www.zakon.kz/api/all-news-ajax/?pn=1&pSize=150", headers=headers, ) #(proxies=proxies)

    news = response.json()
    data_list = news.get('data_list')
    index = data_list[0]  # Это позволяет выбрать сегодняшние новости
    # В json. который мы получаем с сайта, новости определены по дате,
    # и всегда, сегодняшние новости будут под первым индексом, его и берем
    today_all_news = index['news_list']

    # Формирует ссылки на сегодняшние новости и записывает их в txt, в директорию, где расположен скрипт
    today_news_url = []
    for alias_link in today_all_news:
        news_url = 'https://www.zakon.kz/' + alias_link.get('alias')
        today_news_url.append(news_url)

        with open("news_link.txt", "w", encoding="utf-8") as file:
            for today_news_link in today_news_url:
                file.write(f"{today_news_link}\n")


# Функция читатет файл.txt, проходит по ссылкам и собирает данные
def get_data(file_path):  # путь до файла
    with open(file_path) as file:
        urls_list = [today_news_urls.strip() for today_news_urls in file.readlines()] # читает файл и сохраняет ссылки обратно в список

    result_list = []
    count = 1
    urls_count = len(urls_list)
    # Проходит по ссылкам и собирает данные
    for today_news_urls in urls_list:
        response = requests.get(url=today_news_urls, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        # Обработка исключений, если вдруг не будет одного из элементов
        try:
            date_name = soup.find(class_="date").text.strip()  # Забирает дату
        except Exception as _ex:
            date_name = None

        try:
            title_name = soup.find("h1").text.strip()  # Забирает заголовки
        except Exception as _ex:
            title_name = None

        try:
            content_name = soup.find(class_="content").text.strip()  # Забирает полный текст
        except Exception as _ex:
            content_name = None

        # Код для коментариев не писал, так как не было смысла

        # Записывает данные в список
        result_list.append(
            {
                "Дата": date_name,
                "Заголовок": title_name,
                "Полный текст ": content_name
            }
        )
        # Рандомная пауза между запросами, на всякий случай
        time.sleep(random.randrange(1, 3))

        if count % 10 == 0:  # на каждой 10 итерации засыпаем на 4-5 секунд
            time.sleep(random.randrange(4, 5))

        print(f"[+] Processed: {count}/{urls_count}")  # Выводит процесс сбора данных в терминал

        count += 1  # отвечает за паузу на каждой 10 итерации

    # Окончательный json файл с данными
    with open("today_all_news.json", "w", encoding="utf-8") as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)


# Можно сначала закаментить get_data, и запустить collect_data(), после того как получим txt файл с ссылками,
# указываем до него путь в get_data(file_path=''), комментим collect_data(), и запускаем снова скрипт.
# Делать не обязательно, если сразу указать путь куда сохранится файл(сохраняется в дирикторию проекта)
@retry
def main():
    collect_data()
    get_data(file_path='C:/Users/mmrmm/Desktop/parser/news_link.txt')  # Указываем свой путь до txt документа с ссылками


if __name__ == "__main__":
    main()
