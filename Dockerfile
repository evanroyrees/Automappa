FROM condaforge/mambaforge:latest

COPY environment.yml /tmp/environment.yml
RUN mamba env update -n base -f /tmp/environment.yml && \
    mamba clean --all --force-pkgs-dirs --yes

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN python -m pip install . --ignore-installed --no-deps -vvv

# Create an unprivileged user for automappa celery worker
RUN adduser --disabled-password --gecos '' automappa

# CMD ["automappa", "-h"]