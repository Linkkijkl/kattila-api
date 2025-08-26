FROM python:3.12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN uv pip install --system --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# See <https://fastapi.tiangolo.com/deployment/docker/#behind-a-tls-termination-proxy>
CMD ["fastapi", "run", "app/main.py", "--proxy-headers", "--workers", "1", "--port", "5100", "--host", "0.0.0.0"]
