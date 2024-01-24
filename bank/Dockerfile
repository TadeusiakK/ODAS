FROM python:3.12.1-bullseye

ENV PYTHONBUFFERED=1

WORKDIR /djangoapp

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD python manage.py runserver 0.0.0.0:8000

EXPOSE 8000