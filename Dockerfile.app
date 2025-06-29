FROM python:3.11-slim

WORKDIR /app

COPY app.py .

RUN apt-get update && apt-get install -y curl
RUN pip install flask

CMD ["python", "app.py"]