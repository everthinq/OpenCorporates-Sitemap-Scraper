# Engineering Challenge: OpenCorporates Sitemap Scraper
[https://gist.github.com](https://gist.github.com/everthinq/9a9ea4d99e5016e22a17baa9e309572b)

------------------------------------------------------
## Description
Scrape all US companies that are identified by URLs like `/companies/us_XX/` where XX is the state code.

------------------------------------------------------
## 🧩 Service Overview

| Service    | Role     | Description |
|------------|----------|-------------|
| `redis`    | Queue    | In-memory store used for sharing sitemap links between scripts and spiders. |
| `db`       | Database | PostgreSQL instance storing the final scraped data. |
| `init_run` | Seeder   | One-time script that pushes sitemap links into Redis. |
| `scrapy`   | Spider   | Runs the Scrapy spider that pulls links from Redis and stores data in PostgreSQL. |

------------------------------------------------------
## Installation
1. Clone the repository:
    ```sh 
    git clone https://github.com/everthinq/OpenCorporates-Sitemap-Scraper.git
   ```
2. Install docker: https://www.docker.com/
------------------------------------------------------
## How to run
1. Go to the project directory with `docker-compose.yml`, for example:
   ```sh 
   cd ~/Projects/yourfolder
   ```
2. Run this to start distrubuted scraping
   ```sh 
   docker compose up --scale scrapy=10
   ```
------------------------------------------------------
## Watch the video explanation of my solution:
<a href="https://www.youtube.com/watch?v=lMHiTUTG_XA" target="_blank">
  <img src="https://img.youtube.com/vi/lMHiTUTG_XA/maxresdefault.jpg" alt="Watch the video" width="600">
</a>