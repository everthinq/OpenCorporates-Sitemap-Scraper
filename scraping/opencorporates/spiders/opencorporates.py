import scrapy
import gzip
import time
import xml.etree.ElementTree as xml_tree

from io import BytesIO
from scrapy_redis.spiders import RedisSpider
from py_mini_racer import MiniRacer
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
        # proxy = self.get_random_proxy()
        # proxy = self.get_regular_proxy()

        script = response.xpath("//script[1]/text()").get()

        # self.logger.info(f"script: {script}")

        js_code = self.extract_js_code(script)
        key = self.solve_js_challenge(js_code)

        # Re-request the sitemap with the solved cookie
        time.sleep(1)  # Wait to ensure the cookie is set properly
        yield scrapy.Request(
            url=response.url,
            callback=self.write_into_db,
            cookies={"KEY": key},
            dont_filter=True,
            meta={"cookie_key": key},
        )

    def write_into_db(self, response: scrapy.http.Response) -> None:
        """Write urls into the database."""
        self.logger.info(f"writing_into_db response url: {response.url}")
        try:
            xml_data = self.read_gzip(response)
            self.logger.info(f"xml_data: {xml_data[:10]}")

            for url in xml_data:
                if "companies/us" in url:
                    yield {"url": url}
        except Exception as e:
            self.logger.error(f"Error reading gzip: {e}. Retrying with cookie.")
            time.sleep(1)
            yield scrapy.Request(
                url=response.url,
                callback=self.parse,
                cookies={"KEY": response.meta["cookie_key"]},
                dont_filter=True,
                meta={
                    "cookie_key": response.meta["cookie_key"],
                    # "proxy": response.meta["proxy"],
                },
            )
        # self.logger.info(f"xml_data: {xml_data[:10]}")

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

    def extract_js_code(self, js_code: str) -> str:
        """Extract and clean the JavaScript code from the response."""
        js_code = (
            js_code.replace("<!--", "").replace("//-->", "").strip()
        )  # replace <!-- and //--> with empty string
        js_code = (
            js_code.replace('{ document.cookie="KEY="+', " return ")
            .replace("document.location.reload(true); }", "")
            .replace(";path=/;", "")
        )  # replace the cookie setting part with return statement
        return js_code

    def solve_js_challenge(self, js_code: str) -> str:
        """Run the JavaScript code via py_mini_racer (embedded V8 for Python) to get the cookie value."""
        ctx = MiniRacer()
        ctx.eval(js_code)
        key = ctx.call("go")
        return key
