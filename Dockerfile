FROM python:3.9-alpine

# Get bash
RUN apk add --no-cache bash
RUN pip install docker-compose

WORKDIR /app

# Install requirements
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt && \
    rm -f requirements.txt

RUN mkdir -p /app/hooks/

# Run Server 
COPY server.py ./server.py
CMD ["python", "server.py"]
EXPOSE 8000
