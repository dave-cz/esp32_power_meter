#
# docker image build -t esp32server .
# docker run --rm -d -p 3033:3033 --name=esp32server esp32server
#
FROM python:3.8-slim-buster

WORKDIR /usr/src/app

COPY . .

RUN apt-get -y update
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

ENV PYTHONWARNINGS="ignore:Unverified HTTPS request"

EXPOSE 3033

CMD ["python3", "./server.py"]
