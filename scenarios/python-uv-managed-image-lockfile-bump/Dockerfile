FROM python:3.12-alpine
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY app ./app
CMD ["python", "-m", "app.main"]