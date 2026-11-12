FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -m mizan
COPY backend/ .
COPY regulatory/ /app/regulatory/
RUN mkdir -p /app/data/evidence && chown -R mizan:mizan /app
USER mizan
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
