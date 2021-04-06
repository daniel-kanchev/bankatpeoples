import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankatpeoples.items import Article


class bankatpeoplesSpider(scrapy.Spider):
    name = 'bankatpeoples'
    start_urls = ['https://www.bankatpeoples.com/home/misc/news/']

    def parse(self, response):
        links = response.xpath('//ul[@class="blog-list"][li]/li/a/@href').getall()
        yield from response.follow_all(links, self.parse_news, dont_filter=True)

    def parse_news(self, response):
        links = response.xpath('//h2/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@role="main"]//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//h1/text()').get()
        if date:
            date = date.split()[-1]

        content = response.xpath('//div[@class="content"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
