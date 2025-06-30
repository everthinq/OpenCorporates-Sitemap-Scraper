FROM python:3-alpine

# Create app directory
WORKDIR /usr/src/app

# Install system dependencies for py_mini_racer
RUN apk add --no-cache \
    libatomic \
    build-base \
    linux-headers \
    libffi-dev \
    musl-dev \
    gcc \
    g++

# Install app dependencies
COPY requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir -r ./requirements.txt

# Copy source code
COPY . ./