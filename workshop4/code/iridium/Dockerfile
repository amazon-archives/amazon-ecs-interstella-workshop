FROM ubuntu:14.04

ENV PRODUCT iridium

RUN apt-get -y update

RUN apt-get -y install \
  git \
  wget \
  python-dev \
  python-virtualenv \
  libffi-dev \
  libssl-dev

WORKDIR /root

RUN wget https://bootstrap.pypa.io/get-pip.py \
  && python get-pip.py

WORKDIR interstella

RUN virtualenv ${PRODUCT}

WORKDIR ${PRODUCT}

RUN bin/pip install --upgrade pip && \
    bin/pip install requests[security]

COPY ./requirements.txt .

RUN bin/pip install -r requirements.txt

COPY ./$PRODUCT.py .

EXPOSE 5000

ENTRYPOINT ["bin/python", "iridium.py"]
