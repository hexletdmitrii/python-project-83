### Hexlet tests and linter status:
[![Actions Status](https://github.com/hexletdmitrii/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/hexletdmitrii/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/fba08cd3976c122289d8/maintainability)](https://codeclimate.com/github/hexletdmitrii/python-project-83/maintainability)

https://page-analyzer-izgx.onrender.com

 Page Analyzer — это проект для анализа веб-страниц.

 ## Установка

  1. **Клонируйте репозиторий:**

     ```bash
     git clone https://github.com/hexletdmitrii/python-project-83.git
     cd page_analyzer
     ```

  2. **Установите Poetry:**

     Убедитесь, что у вас установлен Poetry. Если нет, вы можете установить его, следуя [официальной инструкции](https://python-poetry.org/docs/#installation).

  3. **Установите зависимости:**

     ```bash
     make install
     ```

  ## Сборка

  Чтобы собрать проект, выполните:

  ```bash
  make build
  ```

  ## Публикация

  Для тестовой публикации пакета выполните:

  ```bash
  make publish
  ```

  ## Линтинг

  Чтобы проверить код с помощью Flake8, выполните:

  ```bash
  make lint
  ```

  ## Разработка

  Для запуска сервера разработки Flask выполните:

  ```bash
  make dev
  ```

  Сервер будет запущен на `http://127.0.0.1:5000`.

  ## Запуск в продакшене

  Для запуска приложения в продакшене с использованием Gunicorn выполните:

  ```bash
  make start
  ```

  По умолчанию сервер будет доступен на `http://0.0.0.0:8000`. Вы можете изменить порт, задав переменную окружения `PORT`:

  ```bash
  make start PORT=5000
  ```



