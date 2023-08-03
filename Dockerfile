FROM python:3.11.1-slim-buster
ENV PYTHONUNBUFFERED=1

WORKDIR /ecopol

COPY . /ecopol

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

