FROM python:3.7

COPY ./requirements.txt /work/requirements.txt
RUN pip install -r /work/requirements.txt

WORKDIR /work
COPY ./src /work/src

CMD ['train']
