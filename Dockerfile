FROM docker:20.10-dind

# Get requirements
RUN apk add --no-cache python3 openssl-dev libffi-dev make git build-base python3-dev py3-pip libgcc bash curl make cargo gcc libc-dev rust
RUN pip3 install docker-compose

WORKDIR /app

# Install requirements
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt && \
    rm -f requirements.txt

RUN mkdir -p /app/hooks/

# Run Server 
COPY server.py ./server.py
CMD ["python3", "server.py"]
EXPOSE 8000
