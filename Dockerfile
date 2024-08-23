FROM python:3.8

COPY . /app

WORKDIR /app

RUN apt-get update
RUN apt-get install -y libgl1-mesa-glx

RUN pip install -r requirements.txt

CMD python3 ./app/main.py