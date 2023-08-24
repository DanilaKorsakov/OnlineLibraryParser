import os
import pathlib

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


def download_txt(response, filename, dest_folder, folder='books/'):

    full_path = f'{dest_folder}/{folder}'

    pathlib.Path(full_path).mkdir(parents=True, exist_ok=True)

    file_path = os.path.join(full_path, f'{sanitize_filename(filename)}.txt')

    with open(file_path, 'wb') as file:
        file.write(response.content)


def download_image (url,  dest_folder, folder='images/'):

    full_path = f'{dest_folder}/{folder}'

    pathlib.Path(full_path).mkdir(parents=True, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    filename = urlsplit(url).path.split('/')[-1]
    filepath = os.path.join(full_path,filename)

    with open(unquote(filepath), 'wb') as file:
        file.write(response.content)