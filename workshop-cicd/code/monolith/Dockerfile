FROM gliderlabs/alpine:3.3

RUN apk add --update \
    python \
    python-dev \
    git \
    wget \
    libffi-dev \
    gcc

WORKDIR /root

ENV PRODUCT monolith

RUN wget https://bootstrap.pypa.io/get-pip.py \
  && python get-pip.py && pip install virtualenv

WORKDIR interstella

RUN virtualenv ${PRODUCT}

WORKDIR ${PRODUCT}

#RUN bin/pip install --upgrade pip && \
#    bin/pip install requests[security]

COPY ./requirements.txt .

RUN bin/pip install -r requirements.txt

COPY ./monolith.py .

EXPOSE 5000

ENTRYPOINT ["bin/python", "monolith.py"]


