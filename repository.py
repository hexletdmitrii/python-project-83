import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor
import requests
from bs4 import BeautifulSoup


class Url_sql():

    def __init__(self, conn=None):
        load_dotenv()
        self.database_url = os.getenv('DATABASE_URL')
        if not conn:
            self.conn = psycopg2.connect(self.database_url)
        else:
            self.conn = psycopg2.connect(conn)

    def create_table(self):
        with self.conn.cursor() as curr:
            curr.execute("""
                         CREATE TABLE IF NOT EXISTS urls
                         (id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                          name VARCHAR(255) NOT NULL,
                          created_at TIMESTAMP NOT NULL DEFAULT LOCALTIMESTAMP);
                         """)
            curr.execute("""
                         CREATE TABLE IF NOT EXISTS url_checks
                         (id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                         url_id BIGINT NOT NULL,
                         status_code INT,
                         h1 VARCHAR(255),
                         title VARCHAR(255),
                         description VARCHAR(255),
                        created_at TIMESTAMP NOT NULL DEFAULT LOCALTIMESTAMP);
                         """)
            self.conn.commit()
            print('Таблица успешно создана')

    def add_url(self, name: str) -> int:
        with self.conn.cursor() as curr:
            curr.execute("""
                        INSERT INTO urls (name) VALUES (%s) RETURNING id;
                         """, (name,))
            id = curr.fetchone()[0]
            self.conn.commit()
            return id

    def add_check(self, url_id):
        try:
            response = requests.get(self.show_url(id=url_id, checks=False)[0]['name'])
            if response.status_code != 200:
                return
            else:
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title').text if soup.find('title') else None
                h1 = soup.find('h1').text if soup.find('h1') else None
                description = soup.find('meta', attrs={'name': 'description'})['content']
        except :
            return
        with self.conn.cursor() as curr:
            curr.execute("""
                        INSERT INTO url_checks
                        (url_id, status_code, h1, title, description)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id;
                         """, (url_id, 200, h1, title, description))
            id = curr.fetchone()[0]
            self.conn.commit()
            return id

    def show_url(self, id: int = None, name: str = None, checks: bool = True):
        with self.conn.cursor(cursor_factory=DictCursor) as curr:
            if not id and not name:
                curr.execute("""
                             SELECT id, name, created_at
                             FROM urls ORDER by created_at DESC;
                             """)
            elif id and not name:
                curr.execute("""
                         SELECT id, name, created_at
                         FROM urls WHERE id = %s
                         ORDER by created_at DESC;
                         """, (id, ))
            elif not id and name:
                curr.execute("""
                         SELECT id, name, created_at
                         FROM urls WHERE name = %s
                         ORDER by created_at DESC;
                         """, (name, ))
            result = []
            for item in curr:
                data = {'id': item['id'],
                        'name': item['name'],
                        'created_at': item['created_at']}
                if checks:
                    data['checks'] = self.show_checks(url_id=item['id'])
                result.append(data)
        return result

    def show_checks(self, url_id: int = None):
        with self.conn.cursor(cursor_factory=DictCursor) as curr:
            curr.execute("""
                        SELECT * FROM url_checks
                        WHERE url_id = %s
                        ORDER BY created_at DESC;
                         """, (url_id,))
            result = []
            for item in curr:
                result.append(item)
            return result

    def update(
            self,
            id: int = None,
            name: str = None,
            clear_table: bool = False
    ):

        with self.conn.cursor(cursor_factory=DictCursor) as curr:
            if clear_table:
                curr.execute("DROP TABLE urls")
                curr.execute("DROP TABLE url_checks")
                self.create_table()
            elif id and name is None:
                curr.execute(
                    "DELETE FROM urls WHERE id = %s RETURNING id;", (id,)
                )
            elif id and name:
                curr.execute(
                    "UPDATE urls SET name = %s WHERE id = %s RETURNING id;",
                    (name, id,))
        self.conn.commit()
        return id


if __name__ == "__main__":
    sql = Url_sql()
    sql.update(clear_table=True)
