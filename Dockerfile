FROM condaforge/mambaforge:latest

COPY environment.yml /tmp/environment.yml
RUN mamba env update -n base -f /tmp/environment.yml && \
    mamba clean --all --force-pkgs-dirs --yes

COPY . /usr/src/app
WORKDIR /usr/src/app

RUN python -m pip install . --ignore-installed --no-deps -vvv

# Create an unprivileged user for automappa celery worker
RUN adduser --disabled-password --gecos '' automappa
RUN mkdir -p /usr/src/app/uploads && \
    chown -R automappa:automappa /usr/src/app

# CMD ["automappa", "-h"]