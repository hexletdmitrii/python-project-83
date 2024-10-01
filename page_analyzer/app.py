from flask import Flask, render_template, url_for, redirect, request, flash
import os
from urllib.parse import urlparse
from repository import Url_sql
import validators

repo = Url_sql()
# load_dotenv()
# database_url = os.getenv('DATABASE_URL')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def show_urls():
    urls = repo.show_url()
    return render_template("urls.html", urls=urls)


@app.get('/urls/<id>')
def show_url(id):
    url = repo.show_url(id=id)
    checks = repo.show_checks(url_id=id)
    print(checks)
    return render_template("url.html", url=url[0], checks=checks)


@app.post('/urls/<id>/checks')
def check_url(id):
    repo.add_check(url_id=id)
    return redirect(url_for('show_url', id=id))


@app.post('/urls')
def add_url():
    url = request.form['url']
    if not validators.url(url):
        flash('Введите корректный URL! Пример: "http://example.ru"', 'error')
        return redirect(url_for('index'))
    url = urlparse(url)
    base_url = f"{url.scheme}://{url.netloc}/"
    try:
        url_check = repo.show_url(name=base_url)
        if len(url_check) > 0:
            flash(f'{base_url} Уже проверен', 'success')
            url_id = url_check[0]['id']
            return redirect(url_for('show_url', id=url_id))
        url_id = repo.add_url(base_url)
        flash(f'{base_url} Добавлен в базу', 'success')
        return redirect(url_for('show_url', id=url_id))
    except Exception as e:
        flash(f'Ошибка базы данных{e}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
