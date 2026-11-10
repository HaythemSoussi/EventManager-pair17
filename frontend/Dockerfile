FROM python:3.10-slim

WORKDIR /app

COPY ./index.html .
COPY ./server.py .

EXPOSE 80

CMD ["python", "server.py"]
