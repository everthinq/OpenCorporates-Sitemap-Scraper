import psycopg2
import json


class OpencorporatesPipeline:
    def open_spider(self, spider):
        settings = spider.settings.get("POSTGRES")
        self.conn = psycopg2.connect(
            host=settings["host"],
            database=settings["database"],
            user=settings["user"],
            password=settings["password"],
            port=settings["port"],
        )
        self.cur = self.conn.cursor()

        if spider.name == "opencorporates":
            self.cur.execute("DROP TABLE IF EXISTS opencorporates CASCADE")
            self.cur.execute("DROP SEQUENCE IF EXISTS opencorporates_id_seq CASCADE")

            self.cur.execute(
                """
                CREATE TABLE IF NOT EXISTS opencorporates (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    url TEXT UNIQUE
                )
            """
            )

            self.conn.commit()

    def process_item(self, item, spider):
        if spider.name == "opencorporates":
            self.cur.execute(
                """
                INSERT INTO opencorporates (url)
                VALUES (%s)
                ON CONFLICT (url) DO NOTHING
                """,
                (item.get("url"),),
            )
            self.conn.commit()
        return item

    def close_spider(self, spider):
        self.conn.commit()
        self.cur.close()
        self.conn.close()
