import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor
import requests
from bs4 import BeautifulSoup
from flask import flash


class Url_sql():

    def __init__(self, conn=None):
        load_dotenv()
        self.database_url = os.getenv('DATABASE_URL')
        if not conn:
            self.conn = psycopg2.connect(self.database_url)
        else:
            self.conn = psycopg2.connect(conn)

    def make_sql(self, sql: str, sitters: tuple = ()):
        result = []
        errors = {}
        with self.conn.cursor(cursor_factory=DictCursor) as curr:
            try:
                curr.execute(sql, sitters)
                for item in curr:
                    result.append(item)
                self.conn.commit()
            except Exception as e:
                errors['sql'] = e
                flash(f"Ошибка базы данных {errors}", 'danger')
        return result, errors

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

    def add_url(self, name: str):
        sql = "INSERT INTO urls (name) VALUES (%s) RETURNING id;"
        id, errors = self.make_sql(sql=sql, sitters=(name,))
        if not errors:
            id = id[0][0]
        return id, errors

    def add_check(self, url_id):
        sql = "SELECT name FROM urls WHERE id = %s"
        url = self.make_sql(sql=sql, sitters=(url_id,))[0]
        try:
            response = requests.get(url[0]['name'])
            if response.status_code != 200:
                return None, response.status_code
            else:
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title').text[:255] if soup.find('title') else ''
                h1 = soup.find('h1').text[:255] if soup.find('h1') else ''
                description = soup.find('meta', attrs={'name': 'description'})['content'][:255] if soup.find('meta', attrs={'name': 'description'}) else ''
        except Exception as e:
            return None, {'sql': e}
        sql = """INSERT INTO url_checks
                    (url_id, status_code, h1, title, description)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id;"""
        id, errors = self.make_sql(sql=sql, sitters=(url_id, 200, h1, title, description))
        if not errors:
            id = id[0][0]
        return id, errors

    def show_urls(self):
        sql = """SELECT
                urls.id as id,
                urls.name as name,
                url_checks.status_code as status_code,
                MAX(url_checks.created_at) as created_at
                FROM urls LEFT JOIN url_checks
                ON urls.id = url_checks.url_id
                GROUP BY urls.id, urls.name, url_checks.status_code
                ORDER BY MAX(url_checks.created_at) DESC NULLS LAST;
                """
        result, errors = self.make_sql(sql)
        return result, errors

    def show_url(self, id: int = None, name: str = None):
        result = []
        errors = {}
        if id:
            sql = "SELECT * from urls WHERE id = %s"
            result, errors = self.make_sql(sql=sql, sitters=(id,))
        if name:
            sql = "SELECT * from urls WHERE name = %s"
            result, errors = self.make_sql(sql=sql, sitters=(name,))
        if not errors and result:
            result = dict(result[0])
            sql = "SELECT id, status_code, h1, title, description, created_at FROM url_checks WHERE url_id = %s ORDER BY created_at DESC"
            result['checks'], errors = self.make_sql(sql=sql, sitters=(result['id'],))
        return result, errors

    def update(
            self,
            id: int = None,
            name: str = None,
            clear_table: bool = False
    ):

        with self.conn.cursor(cursor_factory=DictCursor) as curr:
            curr.execute("DROP TABLE urls")
            curr.execute("DROP TABLE url_checks")
            self.create_table()


if __name__ == "__main__":
    sql = Url_sql()
    sql.update(clear_table=True)
    # print(sql.show_url(1))
