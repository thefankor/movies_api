FROM python:3.12-slim

WORKDIR /mov_api

COPY . .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]

