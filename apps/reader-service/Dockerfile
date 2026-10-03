FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic
COPY entrypoint.sh .

ENV PYTHONUNBUFFERED=1
EXPOSE 3001
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
