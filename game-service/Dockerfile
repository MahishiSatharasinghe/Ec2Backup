FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV DB_HOST=mysql
ENV DB_USER=root
ENV DB_PASSWORD=root
ENV DB_NAME=gamedb

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
