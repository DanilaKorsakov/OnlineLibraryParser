import requests
import os


def check_for_redirect(book):
    if book.history:
        raise requests.exceptions.HTTPError


if not os.path.exists('books'):
    os.makedirs('books')

for book_number in range(1,11):
    url = f"https://tululu.org/txt.php?id={book_number}"
    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)
        filename = f'books/id{book_number}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)
    except requests.exceptions.HTTPError:
        print("Такой книги нет")




