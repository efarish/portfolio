FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

RUN python create_chroma_db.py

EXPOSE 9090

CMD ["python3", "server.py"]
