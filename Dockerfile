FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /app /tmp/tanf
WORKDIR /app
COPY requirements.txt /app/
RUN curl https://raw.githubusercontent.com/eficode/wait-for/master/wait-for > /app/wait-for ; chmod +x /app/wait-for
RUN apt-get -q update && apt-get -qy install netcat
RUN pip3 install -r requirements.txt
COPY . /app/
