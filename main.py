import requests
import os


if not os.path.exists('books'):
    os.makedirs('books')

for book_number in range(1,11):
    url = f"https://tululu.org/txt.php?id={book_number}"
    response = requests.get(url)
    response.raise_for_status()

    filename = f'books/id{book_number}.txt'
    with open(filename, 'wb') as file:
        file.write(response.content)

