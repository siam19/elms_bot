FROM python:3.12-alpine


WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./app /code/app

CMD ["fastapi", "run", "app/server.py", "--port", "8000"]