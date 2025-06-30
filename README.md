# Engineering Challenge: OpenCorporates Sitemap Scraper
[https://gist.github.com](https://gist.github.com/everthinq/9a9ea4d99e5016e22a17baa9e309572b)

------------------------------------------------------
## Description
Scrape all US companies are identified by URLs like `/companies/us_XX/` where XX is the state code.
------------------------------------------------------
## Installation
1. Clone the repository:
    ```sh 
    git clone https://github.com/everthinq/OpenCorporates-Sitemap-Scraper.git
   ```
2. Install docker: https://www.docker.com/
------------------------------------------------------
## How to run
1. Go to the project directory, for example:
   ```sh 
   cd ~/Projects/Scrapy/books
   ```
2. Run this to start distrubuted scraping
   ```sh 
   docker compose up --scale scrapy=10
   ```