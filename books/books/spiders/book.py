# -*- coding: utf-8 -*-
import scrapy
from books.items import BooksItem


class BookSpider(scrapy.Spider):
    name = 'book'
    allowed_domains = ['books.toscrape.com']
    Q = None

    def start_requests(self):
        self.Q.put('开始采集')
        for page_num in range(1, 51):
            url = 'http://books.toscrape.com/catalogue/page-%d.html' % page_num
            yield scrapy.Request(url)

    def parse(self, response):
        items = BooksItem()
        for book in response.xpath('//article[@class="product_pod"]'):
            items['title'] = book.xpath('./h3/a/@title').extract_first()  # 书本标题
            items['price'] = book.xpath('./div/p[@class="price_color"]/text()').extract_first()  # 书本价格
            review = book.xpath('./p[1]/@class').extract_first()  # 书本评级
            items['review'] = review.split(' ')[-1]
            self.Q.put(f"{items['title']}\n{items['price']}\n{items['review']}\n")
            yield items

    def close(spider, reason):
        spider.Q.put('采集结束')
