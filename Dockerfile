FROM python:3.12-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY adaptive/ adaptive/
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.12-alpine

RUN apk add --no-cache libffi openssl openssh-client sshpass

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY alembic.ini ./
COPY migrations/ migrations/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && gunicorn adaptive.api.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"]
