import os
import json
import pathlib
import argparse
from time import sleep

import requests
from pathvalidate import sanitize_filename
from urllib.parse import unquote, urljoin, urlsplit
from bs4 import BeautifulSoup


def check_for_redirect(book):
    if book.history:
        raise requests.exceptions.HTTPError


def parse_book_page(response, template_url):

    soup = BeautifulSoup(response.text, 'lxml')
    title_text = soup.select_one("#content h1")
    title_name, title_author = title_text.text.split(' :: ')
    title_image = soup.select_one(".bookimage img")['src']
    image_url = urljoin(template_url,title_image)

    book_comments = soup.select(".texts")
    book_comments_text = []
    for book_comment in book_comments:
        book_comments_text.append(book_comment.select_one('.black').text)

    book_genres = soup.select('.d_book a')

    book_genres = [genre_tag.text for genre_tag in book_genres]

    book_page_params = {
        "title":title_name.strip(),
        "author":title_author.strip(),
        "image_url": image_url,
        "comments": book_comments_text,
        "genres": book_genres,
    }

    return book_page_params


def download_txt(response, filename, folder='books/'):

    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    file_path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')

    with open(file_path, 'wb') as file:
        file.write(response.content)


def download_image (url,  folder='images/'):

    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    filename = urlsplit(url).path.split('/')[-1]
    filepath = os.path.join(folder,filename)

    with open(unquote(filepath), 'wb') as file:
        file.write(response.content)


parser = argparse.ArgumentParser(
    description='Программа получает информацию по книгам с сайта http://tululu.org, а также скачивает их текст и картинку'
)
parser.add_argument("--start_page", type=int, help="Начальная страница для скачивания книг", default=1)
parser.add_argument("--end_page", type=int, help="Последняя страница для скачивания книг", default=11)
args = parser.parse_args()

template_url = 'https://tululu.org/'

book_txt_url= "https://tululu.org/txt.php"

books_archive = []

for page_number in range(args.start_page, args.end_page):
    url = "https://tululu.org/l55/"
    if page_number !=1:
        url = f"{url}/{page_number}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    table_line = soup.select(".d_book")


    for book in table_line:

        table_link = book.select_one('a')
        book_url = urljoin(template_url,table_link['href'])

        try:

            response = requests.get(book_url)
            response.raise_for_status()

            check_for_redirect(response)

            book_parameters = parse_book_page(response,book_url)

            books_archive.append(book_parameters)

            download_image(book_parameters['image_url'])

            book_id = book_url.split('/')[3]

            book_number = book_id[1:]

            params = {"id": book_number}

            book_response = requests.get(book_txt_url,params)
            book_response.raise_for_status()

            check_for_redirect(book_response)

            download_txt(book_response,book_parameters['title'])

        except requests.exceptions.HTTPError:
            print("Такой книги нет")
        except requests.exceptions.ConnectionError:
            print("Повторное подключение к серверу")
            sleep(20)


with open("books.json", "w", encoding='utf8') as my_file:
    json.dump(books_archive, my_file, ensure_ascii=False)


