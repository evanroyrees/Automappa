FROM condaforge/miniforge3:4.11.0-0
# https://github.com/mamba-org/micromamba-docker

COPY requirements.txt /tmp/requirements.txt

RUN conda install \
    --name base \
    --channel conda-forge --channel bioconda \
    --yes  \
    python=3.7 \
    --file=/tmp/requirements.txt

RUN conda install \
    --name base \
    --channel anaconda --channel conda-forge \
    --yes  git

RUN git clone -b large-data-mode https://github.com/WiscEvan/Autometa.git /tmp/Autometa
RUN conda install --name base -c conda-forge -c bioconda --file=/tmp/Autometa/requirements.txt -y
WORKDIR /tmp/Autometa
RUN /opt/conda/bin/python setup.py install

RUN conda clean --all --yes

COPY . .

# ENTRYPOINT /opt/conda/bin/python index.py