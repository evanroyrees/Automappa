FROM continuumio/miniconda3:4.6.14-alpine

# RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt .
# WORKDIR /autometa-app
RUN /opt/conda/bin/pip install -r requirements.txt
COPY . /autometa-app
ENV PATH /autometa-app:$PATH
# CMD ["python","index.py"]
