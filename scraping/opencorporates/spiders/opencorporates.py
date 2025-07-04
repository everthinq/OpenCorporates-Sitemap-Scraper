import scrapy
import gzip
import time
import xml.etree.ElementTree as xml_tree

from io import BytesIO
from scrapy_redis.spiders import RedisSpider
from random import choice


class OpencorporatesSpider(RedisSpider):
    name = "opencorporates"
    redis_key = "opencorporates:get_xml"

    custom_settings = {
        "ROTATING_PROXY_LIST": [
            f"http://teilcwwn-{i}:v0dwwr6f725f@p.webshare.io:80" for i in range(1, 251)
        ],
        "DOWNLOADER_MIDDLEWARES": {
            "rotating_proxies.middlewares.RotatingProxyMiddleware": 98,
            "rotating_proxies.middlewares.BanDetectionMiddleware": 99,
        },
    }

    def parse(self, response: scrapy.http.Response) -> scrapy.Request:
        # self.logger.info(f"response: {response.text}")

        self.logger.info(f"writing into db response url: {response.url}")
        try:
            xml_data = self.read_gzip(response)
            self.logger.info(f"xml_data: {xml_data[:10]}")

            for url in xml_data:
                if "companies/us" in url:
                    yield {"url": url}
        except Exception as e:
            self.logger.error(f"Error reading gzip: {e}. Retrying with time.sleep(1).")
            time.sleep(1)
            yield scrapy.Request(
                url=response.url,
                callback=self.parse,
                dont_filter=True,
            )

    def read_gzip(self, response: scrapy.http.Response) -> list[str]:
        """Read and decompress a gzip or XML file with <url><loc> entries."""
        with gzip.GzipFile(fileobj=BytesIO(response.body)) as f:
            xml_data = f.read().decode("utf-8")

        root = xml_tree.fromstring(xml_data)

        # Define XML namespace (for <url> and <loc> elements)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        # Extract all <loc> inside <url>
        urls = [elem.text for elem in root.findall("sm:url/sm:loc", ns)]

        return urls
