FROM python:3.12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN uv pip install --system --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["fastapi", "dev", "app/main.py", "--port", "5100", "--host", "0.0.0.0"]
