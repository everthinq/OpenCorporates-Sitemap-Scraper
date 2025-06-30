import requests_html as req
import time
import gzip
import xml.etree.ElementTree as xml_tree
import redis

from io import BytesIO
from py_mini_racer import MiniRacer
from random import choice

BASE_URL = "https://opencorporates.com/sitemap.xml.gz"

session = req.HTMLSession()


def main():
    """Main function to fetch and process the sitemap XML from OpenCorporates."""
    proxy = get_random_proxy()
    r = session.get(BASE_URL, proxies=proxy)
    # print(r.content)

    js_code = get_js_code(r)
    key = run_js_code(js_code)

    time.sleep(1)  # if you don't wait, the cookie will not be set properly
    r = session.get(BASE_URL, cookies={"KEY": key}, proxies=proxy)
    # print(r.content)

    urls = read_gzip(r)
    print(urls[:10])  # Print first 10 URLs for debugging
    push_into_redis(urls[100:200])


def get_random_proxy() -> str:
    ROTATING_PROXY_LIST = (
        [f"http://ircfldbm-{i}:2keltj14xtop@p.webshare.io:80" for i in range(1, 1000)],
    )
    proxy = choice(ROTATING_PROXY_LIST[0])
    return {"http": proxy, "https": proxy}


def get_js_code(r: req.HTML) -> str:
    """Extract the JavaScript code from the HTML response."""
    js_code = r.html.xpath("//script")
    js_code = js_code[0].text if js_code else None
    js_code = (
        js_code.replace("<!--", "").replace("//-->", "").strip()
    )  # replace <!-- and //--> with empty string
    js_code = (
        js_code.replace(' { document.cookie="KEY="+', " return ")
        .replace("; document.location.reload(true); }", "")
        .replace(";path=/;", "")
    )  # replace the cookie setting part with return statement
    return js_code


def run_js_code(js_code: str) -> str:
    """Run the JavaScript code via py_mini_racer (embedded V8 for Python) to get the cookie value."""
    ctx = MiniRacer()

    ctx.eval(js_code)
    key = ctx.call("go")

    return key


def read_gzip(r: req.HTML) -> list[str]:
    """Read and decompress a gzip file."""
    with gzip.GzipFile(fileobj=BytesIO(r.content)) as f:
        xml_data = f.read().decode("utf-8")

    root = xml_tree.fromstring(xml_data)

    # Define the XML namespace
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    # Extract all <loc> text
    urls = [elem.text for elem in root.findall("sm:sitemap/sm:loc", ns)]
    return urls


def push_into_redis(urls: list) -> None:
    """Push URLs into Redis."""
    redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)
    redis_client.lpush(
        "opencorporates:get_xml",
        *urls,
    )


if __name__ == "__main__":
    main()
