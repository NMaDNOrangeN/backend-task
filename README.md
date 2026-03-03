Создание venv (Один раз при установке проекта)
`python -m venv .venv`

Активация venv
`.venv\Scripts\activate`

Установка зависимости
`pip install -r requirements.txt`

Запуск проекта в режиме dev
`python -m fastapi dev main.py`

Запуск проекта в режиме prod
`python -m fastapi run main.py`
