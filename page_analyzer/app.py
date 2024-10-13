from flask import Flask, render_template, url_for, redirect, request, flash
import os
from urllib.parse import urlparse
from page_analyzer.repository import Url_sql
import validators
from datetime import datetime
# from dotenv import load_dotenv


# load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.template_filter('format_date')
def format_date(value):
    date_object = datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S.%f")
    return date_object.strftime("%Y-%m-%d")


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def show_urls():
    data, errors = Url_sql().show_urls()
    return render_template("urls.html", urls=data)


@app.get('/urls/<int:id>')
def show_url(id):
    data, errors = Url_sql().show_url(id)
    if not data:
        return redirect(url_for('index'))
    return render_template("url.html", url=data)


@app.post('/urls/<id>/checks')
def check_url(id):
    url_id, errors = Url_sql().add_check(id)
    if errors or not url_id:
        flash(f'Произошла ошибка при проверке {errors}', 'danger')
    else:
        flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id=id))


@app.post('/urls')
def add_url():
    url = request.form['url']
    if not validators.url(url):
        flash('Некорректный URL', 'danger')
        return redirect(url_for('index')), 422
    url = urlparse(url)
    base_url = f"{url.scheme}://{url.netloc}/"
    data, errors = Url_sql().show_url(name=base_url)
    if errors:
        return redirect(url_for('index'))
    if data:
        flash('Страница уже существует', 'success')
        return redirect(url_for('show_url', id=data['id']))
    url_id, errors = Url_sql().add_url(base_url)
    if errors:
        return redirect(url_for('index'))
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url', id=url_id))


if __name__ == '__main__':
    app.run(debug=True)
