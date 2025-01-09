import os
import json
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://m128axtest:0997943465@m128ax.58sei.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client.quotes_db


def run_spider(spider_name):
    process = CrawlerProcess(get_project_settings())
    process.crawl(spider_name)
    process.start()

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


if __name__ == "__main__":
    # Видаляємо старі файли
    if os.path.exists("quotes.json"):
        os.remove("quotes.json")
    if os.path.exists("authors.json"):
        os.remove("authors.json")

    # Запускаємо павука
    run_spider("quotes")

    # Завантаження quotes.json у колекцію "quotes"
    load_json_to_mongo("quotes.json", "quotes")

    # Завантаження authors.json у колекцію "authors"
    load_json_to_mongo("authors.json", "authors")

    print("Завантаження завершено!")
