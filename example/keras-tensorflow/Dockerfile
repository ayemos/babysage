FROM tensorflow/tensorflow:1.12.0-py3

ENV LANG=ja_JP.UTF-8
ENV LC_ALL=ja_JP.UTF-8

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /work
COPY . /work

ENV PATH=/work:${PATH}

CMD ["train"]
