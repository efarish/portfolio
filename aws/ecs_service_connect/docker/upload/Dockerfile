FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

RUN mkdir /app/uploads

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
