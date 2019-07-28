FROM conda/miniconda3:latest

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /autometa-app
ENV PATH /autometa-app:$PATH
