import requests
import os
import argparse
import pathlib

from pathvalidate import sanitize_filename
from urllib.parse import unquote, urljoin, urlsplit
from bs4 import BeautifulSoup


def check_for_redirect(book):
    if book.history:
        raise requests.exceptions.HTTPError


def parse_book_page(response):

    soup = BeautifulSoup(response.text, 'lxml')
    title_text = soup.find(id="content").find('h1')
    title_name, title_author = title_text.text.split(' :: ')
    title_image = soup.find(class_="bookimage").find('img')['src']
    image_url = urljoin('http://tululu.org',title_image)

    book_comments = soup.find_all("div", class_="texts")
    book_comments_text = []
    for book_comment in book_comments:
        book_comments_text.append(book_comment.find(class_='black').text)

    book_genres = soup.find("span", class_='d_book').find_all('a')

    book_genres = [genre_tag.text for genre_tag in book_genres]

    book_page_params = {
        "title":title_name.strip(),
        "author":title_author.strip(),
        "image_url": image_url,
        "comments": book_comments_text,
        "genres": book_genres,
    }

    return book_page_params


def download_txt(response, book_number, filename, folder='books/'):

    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    file_path = os.path.join(folder, f'{book_number}. {sanitize_filename(filename)}.txt')

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


def main():

    parser = argparse.ArgumentParser(
        description='Программа получает информацию по книгам с сайта http://tululu.org, а также скачивает их текст и картинку'
    )
    parser.add_argument("start_id", type=int, help="Начальная точка скачивания книг", default=1)
    parser.add_argument("end_id", type=int, help="Конечная точка скачивания книг", default=11)
    args = parser.parse_args()

    for book_number in range(args.start_id, args.end_id):


        book_url = f"https://tululu.org/txt.php?id={book_number}"
        site_url = f'https://tululu.org/b{book_number}/'

        try:
            response = requests.get(book_url)
            response.raise_for_status()

            check_for_redirect(response)

            book_response = requests.get(site_url)
            book_response.raise_for_status()

            check_for_redirect(book_response)

            book_info = parse_book_page(book_response)

            download_txt(response,book_number, book_info['title'])
            download_image(book_info['image_url'])

        except requests.exceptions.HTTPError:
            print("Такой книги нет")


if __name__ == '__main__':
    main()

