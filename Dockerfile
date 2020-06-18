FROM ubuntu:19.10

COPY loader.py /loader.py

RUN apt-get update && \
    apt-get install -y \
    git python3-pip
    
# COPY ./requirements.txt /requirements.txt
COPY ./loader.py /loader.py
COPY ./config.json /config.json
WORKDIR /

RUN pip3 install twint pymongo

ENV mongoCS="mongodb://172.17.0.2:27017"
ENTRYPOINT ["python3", "loader.py"]