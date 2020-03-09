FROM node:6-jessie

RUN apt-get update && apt-get install -y calibre
RUN npm install -g gitbook-cli

WORKDIR /cm
RUN curl -L https://github.com/opencontrol/compliance-masonry/releases/download/v1.1.6/compliance-masonry_1.1.6_linux_amd64.tar.gz | tar zxpf -

# Copy sources
WORKDIR /app
COPY . .

WORKDIR /app/compliance
RUN /cm/compliance-masonry get
RUN /cm/compliance-masonry docs gitbook LATO

WORKDIR /app/compliance/exports
EXPOSE 4000
ENTRYPOINT ["gitbook", "serve"]
