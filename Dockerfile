FROM condaforge/miniforge3:latest

COPY environment.yml ./environment.yml

RUN conda env update -n base -f=environment.yml \
    && conda clean --all --force-pkgs-dirs --yes

# Test command is functional
COPY . /Automappa/
WORKDIR /Automappa/
RUN python -m pip install . --ignore-installed --no-deps -vvv
RUN automappa -h

CMD [ "-h" ]
ENTRYPOINT [ "automappa" ]