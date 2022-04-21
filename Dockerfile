FROM condaforge/miniforge3:latest

COPY environment.yml ./environment.yml

RUN conda install --prune --name base mamba --yes
RUN mamba env update --name base --file=./environment.yml \
    && mamba clean --all --force-pkgs-dirs --yes

# Test command is functional
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN python -m pip install . --ignore-installed --no-deps -vvv
RUN automappa -h

# Create an unprivileged user for running our Python code.
RUN adduser --disabled-password --gecos '' automappa

# CMD [ "-h" ]
# ENTRYPOINT [ "automappa" ]