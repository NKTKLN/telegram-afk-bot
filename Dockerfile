# ===== Stage 1: Assembler =====
FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.1.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
        curl \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --only main --no-interaction --no-ansi

# ===== Stage 2: Final =====
FROM python:3.13-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create an unprivileged user in advance to avoid permission issues
RUN groupadd -g 1000 shrimp && \
    useradd -m -u 1000 -g shrimp shrimp

WORKDIR /app

# Copy only the necessary files from the builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /app /app

# Copy the rest
COPY . .

# Set permissions immediately after copying
RUN chown -R shrimp:shrimp /app

USER shrimp

ENTRYPOINT ["python", "-m", "app.main"]
