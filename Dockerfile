FROM condaforge/miniforge3:latest

COPY environment.yml /tmp/environment.yml
RUN conda install -c conda-forge --name base mamba --yes

RUN mamba env update --name base --file=/tmp/environment.yml \
    && mamba clean --all --force-pkgs-dirs --yes

COPY . /usr/src/app
WORKDIR /usr/src/app
# Create an unprivileged user for running our Python code.
RUN adduser --disabled-password --gecos '' automappa

RUN python -m pip install . --ignore-installed --no-deps -vvv
# Test command is functional
RUN automappa -h

# CMD [ "-h" ]
# ENTRYPOINT [ "automappa" ]