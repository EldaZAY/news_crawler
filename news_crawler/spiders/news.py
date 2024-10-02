import logging

import scrapy
from scrapy import Request
from scrapy.exceptions import NotSupported
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse
import csv
from collections import defaultdict
from scrapy.utils.project import get_project_settings
import http.client

from news_crawler import settings


def clean_url(url):
    return url.removeprefix("https://").removeprefix("http://").removeprefix("www.").removesuffix("/")


class NewsSpider(CrawlSpider):
    name = 'news'

    def __init__(self, sitename=None, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        if sitename is None:
            raise ValueError("sitename is required")
        self.sitename = sitename
        self.allowed_domains = [f'{sitename}.com', f'www.{sitename}.com']
        self.start_urls = [f'https://www.{sitename}.com']

        self.rules = (
            Rule(LinkExtractor(allow=[rf'https?://(www\.)?{self.sitename}.*'], deny_extensions=[],
                               attrs=['href', 'src'], tags=['a', 'img'],),
                 callback='parse_item', follow=True),
        )
        # here all extensions are allowed
        # unwanted types are filtered later after successful fetching pages, based on content-type
        super()._compile_rules()

        self.settings = get_project_settings()
        self.total_urls_extracted = 0
        # self.fetched_urls = set()
        self.unique_urls = set()

        self.fetch_file = open(f'fetch_{self.sitename}.csv', 'w', newline='')
        self.visit_file = open(f'visit_{self.sitename}.csv', 'w', newline='')
        self.urls_file = open(f'urls_{self.sitename}.csv', 'w', newline='')

        self.fetch_writer = csv.writer(self.fetch_file)
        self.visit_writer = csv.writer(self.visit_file)
        self.urls_writer = csv.writer(self.urls_file)

        self.fetch_writer.writerow(['URL', 'Status Code'])
        self.visit_writer.writerow(['URL', 'Size (Bytes)', 'Number of Outlinks', 'Content Type'])
        self.urls_writer.writerow(['URL', 'Indicator'])

        self.fetches_attempted = 0
        self.fetches_succeeded = 0
        self.status_codes = defaultdict(int)
        self.file_sizes = defaultdict(int)
        self.content_types = defaultdict(int)


    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield Request(url, callback=self.parse_item, meta={'depth': 0})

    def parse_item(self, response):
        # update stats: fetches
        self.fetches_attempted += 1
        self.fetch_writer.writerow([response.url, response.status])
        self.status_codes[response.status] += 1

        if response.status // 100 == 2:
            self.fetches_succeeded += 1
            content_type = response.headers.get('Content-Type', b'').decode('utf-8').split(';')[0].strip()
            allowed_types = ['text/html', 'application/pdf', 'application/msword', 'image/']

            if any(content_type.startswith(allowed) for allowed in allowed_types):
                size = len(response.body)
                try:
                    links = response.css('a::attr(href)').getall() + response.css('img::attr(src)').getall()
                except NotSupported:
                    logging.info(f"Non-text content encountered at {response.url}")
                    links = []
                self.visit_writer.writerow([
                    response.url,
                    size,
                    len(links),
                    content_type
                ])
                self.total_urls_extracted += len(links)

                # update stats: content types, file sizes
                self.content_types[content_type] += 1
                if size < 1024:
                    self.file_sizes['< 1KB'] += 1
                elif size < 10 * 1024:
                    self.file_sizes['1KB ~ <10KB'] += 1
                elif size < 100 * 1024:
                    self.file_sizes['10KB ~ <100KB'] += 1
                elif size < 1024 * 1024:
                    self.file_sizes['100KB ~ <1MB'] += 1
                else:
                    self.file_sizes['>= 1MB'] += 1

                for link in links:
                    absolute_url = response.urljoin(link)
                    cleaned_url = clean_url(absolute_url)
                    parsed_url = urlparse(absolute_url)

                    # update stats: whether within allowed domain; unique urls
                    in_domain = parsed_url.netloc in self.allowed_domains
                    self.urls_writer.writerow([absolute_url, 'OK' if in_domain else 'N_OK'])
                    self.unique_urls.add((cleaned_url, 'OK' if in_domain else 'N_OK'))


    def closed(self, reason):
        self.fetch_file.close()
        self.visit_file.close()
        self.urls_file.close()
        self.write_report()

    def write_report(self):
        with open(f'crawl_report_{self.sitename}.txt', 'w') as report:
            report.write("Name: Aiyu Zhang\n")
            report.write("USC ID: 8524183902\n")
            report.write(f"News site crawled: {self.allowed_domains[0]}\n")
            report.write(f"Number of threads: {self.settings.get('CONCURRENT_REQUESTS')}\n\n")

            report.write("Fetch Statistics\n")
            report.write("================\n")
            report.write(f"# fetches attempted: {self.fetches_attempted}\n")
            report.write(f"# fetches succeeded: {self.fetches_succeeded}\n")
            report.write(f"# fetches failed or aborted: {self.fetches_attempted - self.fetches_succeeded}\n\n")

            report.write("Outgoing URLs:\n")
            report.write("==============\n")
            n_unique_urls = len(self.unique_urls)
            n_unique_urls_OK = sum(1 for _, indicator in self.unique_urls if indicator == 'OK')
            report.write(f"Total URLs extracted: {self.total_urls_extracted}\n")
            report.write(f"# unique URLs extracted: {n_unique_urls}\n")
            report.write(f"# unique URLs within News Site: {n_unique_urls_OK}\n")
            report.write(f"# unique URLs outside News Site: {n_unique_urls - n_unique_urls_OK}\n\n")

            report.write("Status Codes:\n")
            report.write("=============\n")
            for status, count in sorted(self.status_codes.items()):
                status_string = http.client.responses.get(status, 'Unknown')
                report.write(f"{status} {status_string}: {count}\n")
            report.write("\n")

            report.write("File Sizes:\n")
            report.write("===========\n")
            for size_range, count in self.file_sizes.items():
                report.write(f"{size_range}: {count}\n")
            report.write("\n")

            report.write("Content Types:\n")
            report.write("==============\n")
            for content_type, count in self.content_types.items():
                report.write(f"{content_type}: {count}\n")
