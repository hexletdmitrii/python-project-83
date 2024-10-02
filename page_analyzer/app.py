from flask import Flask, render_template, url_for, redirect, request, flash
import os
from urllib.parse import urlparse
from repository import Url_sql
import validators

repo = Url_sql()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
repo.create_table()


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def show_urls():
    repo = Url_sql()
    try:
        urls = repo.show_url()
    except Exception as e:
        flash(f"Ошибка базы данных {e}", 'danger')
        urls = []
    return render_template("urls.html", urls=urls)


@app.get('/urls/<int:id>')
def show_url(id):
    repo = Url_sql()
    try:
        url = repo.show_url(id=id)
    except Exception as e:
        flash(f"Ошибка базы данных {e}", 'danger')
        url = []
    # checks = repo.show_checks(url_id=id)
    return render_template("url.html", url=url[0])


@app.post('/urls/<id>/checks')
def check_url(id):
    repo = Url_sql()
    try:
        s = repo.add_check(url_id=id)
        if not s:
            flash('Произошла ошибка при проверке', 'danger')
        else:
            flash('Страница успешно проверена', 'success')
    except Exception as e:
        flash(f"Ошибка базы данных {e}", 'danger')
    return redirect(url_for('show_url', id=id))


@app.post('/urls')
def add_url():
    repo = Url_sql()
    url = request.form['url']
    if not validators.url(url):
        flash('Некорректный URL', 'danger')
        return redirect(url_for('index'))
    url = urlparse(url)
    base_url = f"{url.scheme}://{url.netloc}/"
    try:
        url_check = repo.show_url(name=base_url)
        if len(url_check) > 0:
            flash(f'Страница уже существует', 'success')
            url_id = url_check[0]['id']
            return redirect(url_for('show_url', id=url_id))
        url_id = repo.add_url(base_url)
        flash(f'{base_url} "Страница успешно добавлена"', 'success')
        return redirect(url_for('show_url', id=url_id))
    except Exception as e:
        flash(f'Ошибка базы данных{e}', 'danger')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
