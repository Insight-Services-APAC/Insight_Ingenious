# Basic Docker Configuration
FROM python:3.13-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["python", "ingen_cli.py", "run-rest-api-server"]
