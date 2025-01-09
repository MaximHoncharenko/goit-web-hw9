import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient

BASE_URL = "http://quotes.toscrape.com"

MONGO_URI = "mongodb+srv://m128axtest:0997943465@m128ax.58sei.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client.quotes_db


# Функція для отримання HTML сторінки
def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# Скрапінг цитат та авторів
def scrape_quotes_and_authors():
    quotes = []
    authors = {}
    page = 1

    while True:
        print(f"Завантаження сторінки {page}...")
        url = f"{BASE_URL}/page/{page}/"
        html = get_html(url)
        soup = BeautifulSoup(html, "html.parser")

        quote_elements = soup.select(".quote")
        if not quote_elements:
            break

        for quote_el in quote_elements:
            text = quote_el.select_one(".text").get_text(strip=True)
            author_name = quote_el.select_one(".author").get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote_el.select(".tag")]

            # Додавання цитати до списку
            quotes.append({
                "text": text,
                "author": author_name,
                "tags": tags,
            })

            # Додавання інформації про автора, якщо його ще немає
            if author_name not in authors:
                author_url = BASE_URL + quote_el.select_one("a")["href"]
                author_html = get_html(author_url)
                author_soup = BeautifulSoup(author_html, "html.parser")
                birth_date = author_soup.select_one(".author-born-date").get_text(strip=True)
                birth_place = author_soup.select_one(".author-born-location").get_text(strip=True)
                description = author_soup.select_one(".author-description").get_text(strip=True)

                authors[author_name] = {
                    "fullname": author_name,
                    "birth_date": birth_date,
                    "birth_place": birth_place,
                    "description": description,
                }

        page += 1

    return quotes, authors

# Збереження даних у JSON
def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Функція для завантаження JSON-файлів у колекцію
def load_json_to_mongo(json_file, collection_name):
    collection = db[collection_name]
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        # Видалення існуючих документів (якщо потрібно)
        collection.delete_many({})
        # Додавання нових документів
        if isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)
    print(f"Файл {json_file} завантажено до колекції {collection_name}.")



# Основний код
if __name__ == "__main__":
    quotes, authors = scrape_quotes_and_authors()

    print("Збереження цитат у quotes.json...")
    save_to_json(quotes, "quotes.json")

    print("Збереження авторів у authors.json...")
    save_to_json(list(authors.values()), "authors.json")

    # Завантаження quotes.json у колекцію "quotes"
    load_json_to_mongo("quotes.json", "quotes")

    # Завантаження authors.json у колекцію "authors"
    load_json_to_mongo("authors.json", "authors")

    print("Завантаження завершено!")

    print("Готово!")
