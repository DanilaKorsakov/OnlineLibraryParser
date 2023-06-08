import requests
import os
from bs4 import BeautifulSoup
import pathlib
from pathvalidate import sanitize_filename


def check_for_redirect(book):
    if book.history:
        raise requests.exceptions.HTTPError

def get_book_info(response):

    soup = BeautifulSoup(response.text, 'lxml')
    title_text = soup.find(id="content").find('h1')
    title_name, title_author = title_text.text.split(' :: ')
    return title_name.strip()

def download_txt(response, book_number, filename, folder='books/'):

    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    file_path = os.path.join(folder, f'{book_number}. {sanitize_filename(filename)}.txt')

    with open(file_path, 'wb') as file:
        file.write(response.content)




for book_number in range(1,11):

    book_url = f"https://tululu.org/txt.php?id={book_number}"
    site_url = f'https://tululu.org/b{book_number}/'

    try:
        response = requests.get(book_url)
        response.raise_for_status()

        check_for_redirect(response)

        book_response = requests.get(site_url)
        book_response.raise_for_status()

        check_for_redirect(book_response)

        book_name = get_book_info(book_response)

        download_txt(response,book_number, book_name)

    except requests.exceptions.HTTPError:
        print("Такой книги нет")




