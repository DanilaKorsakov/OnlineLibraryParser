import os
import json
import pathlib
import argparse
from time import sleep

import requests
from urllib.parse import unquote, urljoin, urlsplit
from bs4 import BeautifulSoup

from tools import check_for_redirect,parse_book_page,download_txt,download_image


def main():

    parser = argparse.ArgumentParser(
        description='Программа получает информацию по книгам с сайта http://tululu.org, а также скачивает их текст и картинку'
    )
    parser.add_argument("--start_page", type=int, help="Начальная страница для скачивания книг", default=1)
    parser.add_argument("--end_page", type=int, help="Последняя страница для скачивания книг", default=11)
    parser.add_argument("--dest_folder", type=str, help="путь к каталогу с результатами парсинга: картинкам, книгам, JSON", default='result')
    parser.add_argument("--skip_imgs", help="Не скачивать изображения", action='store_true')
    parser.add_argument("--skip_txt", help="Не скачивать книги", action='store_true')

    args = parser.parse_args()

    pathlib.Path(args.dest_folder).mkdir(parents=True, exist_ok=True)

    book_txt_url= "https://tululu.org/txt.php"
    template_url = "https://tululu.org/l55/"


    books_archive = []

    for page_number in range(args.start_page, args.end_page):
        url = f"{template_url}/{page_number}"
        try:
            response = requests.get(url)
            response.raise_for_status()

            check_for_redirect(response)

            soup = BeautifulSoup(response.text, 'lxml')
            book_content = soup.select(".d_book")


            for book in book_content:

                book_link = book.select_one('a')

                book_url = urljoin('https://tululu.org',book_link['href'])

                try:

                    response = requests.get(book_url)
                    response.raise_for_status()

                    check_for_redirect(response)

                    book_parameters = parse_book_page(response,book_url)

                    books_archive.append(book_parameters)


                    if not args.skip_imgs:
                        download_image(book_parameters['image_url'],args.dest_folder)

                    if not args.skip_txt:
                        book_id = book_url.split('/')[3]

                        book_number = book_id[1:]

                        params = {"id": book_number}

                        book_response = requests.get(book_txt_url,params)
                        book_response.raise_for_status()

                        check_for_redirect(book_response)
                        download_txt(book_response,book_parameters['title'],args.dest_folder)
                except requests.exceptions.ConnectionError:
                    print("Повторное подключение к серверу")
                    sleep(20)
        except requests.exceptions.HTTPError:
            print("Такой книги нет")
        except requests.exceptions.ConnectionError:
            print("Повторное подключение к серверу")
            sleep(20)

    file_path = os.path.join(args.dest_folder,"books.json")

    with open(file_path, "w", encoding='utf8') as my_file:
        json.dump(books_archive, my_file, ensure_ascii=False)


if __name__ == '__main__':
    main()

