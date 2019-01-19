FROM python:3.7.2-slim

WORKDIR /app

COPY . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8080

CMD ["python3", "-u", "server.py"]
