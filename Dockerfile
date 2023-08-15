FROM python:3.11.1-slim-buster
ENV PYTHONUNBUFFERED=1

WORKDIR /ecopol

COPY . ./

RUN pip install --no-cache-dir -r ./requirements.txt
CMD ["gunicorn", "ecopol.wsgi:application", "--bind", "0.0.0.0:8000"]
#EXPOSE 8000

