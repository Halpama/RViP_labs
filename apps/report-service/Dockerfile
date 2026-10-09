FROM python:3.13.7-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY entrypoint.sh .
ENV PYTHONUNBUFFERED=1
EXPOSE 3002
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
