import scrapy
import json


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        # Скрапінг цитат
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("span small.author::text").get(),
                "tags": quote.css("div.tags a.tag::text").getall(),
            }

        # Перехід на наступну сторінку
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def closed(self, reason):
        # Скрапінг авторів
        authors_page = 'http://quotes.toscrape.com/authors/'
        return scrapy.Request(authors_page, self.parse_authors)

    def parse_authors(self, response):
        # Скрапінг авторів
        for author in response.css("div.author-details"):
            yield {
                "name": author.css("h3.author-title::text").get().strip(),
                "birthdate": author.css("span.author-born-date::text").get(),
                "location": author.css("span.author-born-location::text").get(),
                "description": author.css("div.author-description::text").get().strip(),
            }
