FROM golang:1.25-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /go-parser ./cmd/parser

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=builder /go-parser /go-parser
COPY --from=builder /app/config /config
ENTRYPOINT ["/go-parser"]
