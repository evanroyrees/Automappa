FROM mambaorg/micromamba:0.19.1
# https://github.com/mamba-org/micromamba-docker

COPY --chown=micromamba:micromamba requirements.txt /tmp/requirements.txt

RUN micromamba install --name base -c conda-forge -c bioconda -y python=3.7 --file=/tmp/requirements.txt
RUN micromamba install --name base -c anaconda -y git

# https://github.com/mamba-org/micromamba-docker#activating-a-conda-environment-for-run-commands
ARG MAMBA_DOCKERFILE_ACTIVATE=1
RUN git clone -b large-data-mode https://github.com/WiscEvan/Autometa.git /tmp/Autometa \
    && micromamba install --name base -c conda-forge -c bioconda --file=/tmp/Autometa/requirements.txt -y \
    && bash -c "make -C /tmp/Autometa install"

RUN micromamba clean --all --yes

COPY . .

# ENTRYPOINT /opt/conda/bin/python index.py