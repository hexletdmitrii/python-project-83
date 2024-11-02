import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor
from page_analyzer.utils import get_url_params


class Url_sql:

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
        return result, errors

    def add_url(self, name: str):
        sql = "INSERT INTO urls (name) VALUES (%s) RETURNING id;"
        id, errors = self.make_sql(sql=sql, sitters=(name,))
        if not errors:
            id = id[0][0]
        return id, errors

    def add_check(self, url_id):
        sql = "SELECT name FROM urls WHERE id = %s"
        url = self.make_sql(sql=sql, sitters=(url_id,))[0]
        data = get_url_params(url=url)
        if 'error' in data:
            return None, {'sql': data['error']}
        sql = """INSERT INTO url_checks
                    (url_id, status_code, h1, title, description)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id;"""
        id, errors = self.make_sql(
            sql=sql,
            sitters=(
                url_id, 200, data['h1'],
                data['title'], data['description']))
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
            sql = """SELECT id, status_code, h1, title, description, created_at
                     FROM url_checks WHERE url_id = %s
                     ORDER BY created_at DESC"""
            result['checks'], errors = self.make_sql(
                sql=sql,
                sitters=(result['id'],))
        return result, errors
