import argparse
import pathlib
from time import sleep

import requests

from tools import check_for_redirect,parse_book_page,download_txt,download_image


def main():

    parser = argparse.ArgumentParser(
        description='Программа получает информацию по книгам с сайта http://tululu.org, а также скачивает их текст и картинку'
    )
    parser.add_argument("--start_id", type=int, help="Начальная точка скачивания книг", default=1)
    parser.add_argument("--end_id", type=int, help="Конечная точка скачивания книг", default=11)
    parser.add_argument("--dest_folder", type=str, help="путь к каталогу с результатами парсинга: картинкам, книгам, JSON", default='result')
    args = parser.parse_args()

    book_txt_url= "https://tululu.org/txt.php"
    book_url = 'https://tululu.org/b{}/'

    pathlib.Path(args.dest_folder).mkdir(parents=True, exist_ok=True)

    for book_number in range(args.start_id, args.end_id):

        params = {"id": book_number}

        try:
            response = requests.get(book_txt_url,params)
            response.raise_for_status()

            check_for_redirect(response)

            book_response = requests.get(book_url.format(book_number))
            book_response.raise_for_status()

            check_for_redirect(book_response)

            book_parameters = parse_book_page(book_response,book_url)

            download_txt(response, book_parameters['title'],args.dest_folder)
            download_image(book_parameters['image_url'],args.dest_folder)

        except requests.exceptions.HTTPError:
            print("Такой книги нет")
        except requests.exceptions.ConnectionError:
            print("Повторное подключение к серверу")
            sleep(20)


if __name__ == '__main__':
    main()

