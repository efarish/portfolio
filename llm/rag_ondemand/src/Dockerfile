FROM public.ecr.aws/docker/library/python:latest

WORKDIR /app

COPY .env /app
COPY *.py /app
COPY requirements.txt /app
RUN mkdir /app/util
COPY ./util/*.py /app/util


RUN pip3 install -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
