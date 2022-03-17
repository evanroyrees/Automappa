FROM condaforge/miniforge3:latest

COPY environment.yml ./environment.yml

RUN conda env update -n base -f=environment.yml \
    && conda clean --all --force-pkgs-dirs --yes

# Test command is functional
COPY . /Automappa/
WORKDIR /Automappa/
RUN /opt/conda/bin/python index.py -h

CMD [ "-h" ]
ENTRYPOINT [ "/opt/conda/bin/python", "index.py" ]