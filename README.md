# Automappa: An interactive interface for exploration of metagenomes

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/WiscEvan/Automappa?label=latest)
[![Anaconda-Server Install Badge](https://anaconda.org/bioconda/automappa/badges/installer/conda.svg)](https://conda.anaconda.org/bioconda)
[![Anaconda-Server Platforms Badge](https://anaconda.org/bioconda/automappa/badges/platforms.svg)](https://anaconda.org/bioconda/automappa)
[![Anaconda-Server Downloads Badge](https://anaconda.org/bioconda/automappa/badges/downloads.svg)](https://anaconda.org/bioconda/automappa)

| Image Name           | Image Tag       | Status                                                                                                                                                                                                                |
|----------------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `evanrees/automappa` | `main`,`latest` | [![docker CI/CD](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml/badge.svg?branch=main "evanrees/automappa:main")](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml)                                       |
| `evanrees/automappa` | `develop`       | [![develop docker CI/CD](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml/badge.svg?branch=develop "evanrees/automappa:develop")](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml) |

![automappa_demo_920](https://user-images.githubusercontent.com/25933122/158899748-bf21c1fc-6f67-4fd8-af89-4e732fa2edcd.gif)

## Getting Started

- [Install with conda](#install-with-conda)
- [Run `automappa` using docker](#quickstart-using-docker-no-installation-required)
- [Install from source](#install-from-source)
- [Advanced Usage](#advanced-usage)
  - [A breakdown of the docker run wrapper script](#full-docker-run-command-example)
  - [Using a remote Automappa server](#using-a-remote-automappa-server)
  - [Using a remote docker container Automappa server](#using-a-remote-docker-container-automappa-server)

## Install with conda

If you are using `conda` (or `mamba`) as a package manager, you can simply install `automappa` using one of the following one-liners.

### with `conda`

```bash
conda install -c bioconda automappa
```

### with `mamba`

```bash
mamba install -c bioconda automappa
```

After you have installed `automappa`, you can simply run `automappa -h` to see a list of available arguments.

To start the `automappa` app, you must specify your main binning results and respective kingdom's single-copy marker annotations 
generated from an [Autometa analysis](https://www.github.com/KwanLab/Autometa). If you do not yet have these annotations and are 
not sure where to start, I would recommend checking out [Autometa's documentation](https://autometa.readthedocs.io/en/latest/)

### Example `automappa` command

```bash
automappa --binning-main </path/to/bacteria.binning.main.tsv> --markers </path/to/bacteria.markers.tsv>
```

## Quickstart using Docker (No installation required)

 To quickly start exploring your data, run the app using a wrapper script that will run the docker image, `evanrees/automappa:latest`, ([available from Dockerhub](https://cloud.docker.com/repository/docker/evanrees/automappa/tags "Automappa Dockerhub Tags")). Now you can skip installation and start binning, examining and describing! Let the microbial exegesis begin!

### Running with a docker container using `run_automappa.sh`

A docker wrapper is available to run a docker container of `Automappa`.
The only required input for this script is the autometa main binning output table and the respective markers table.

```bash
# First retrieve the script:
curl -o run_automappa.sh https://raw.githubusercontent.com/WiscEvan/Automappa/main/docker/run_automappa.sh
# (make it executable)
chmod a+x run_automappa.sh
```

Now run automappa on autometa binning results using the downloaded script: `run_automappa.sh`.

### Start automappa docker container

***NOTE: This will pull the automappa docker image if it is not already available***

```bash
./run_automappa.sh --binning binning.main.tsv --markers binning.markers.tsv
```

----------------------------------------------------------------------------------------------------

## Install from source

### Installation from source (using `make`)

You can install all of Automappa's dependencies using the Makefile found within the repository.

#### Clone the Automappa repository

```bash
cd $HOME
git clone https://github.com/WiscEvan/Automappa.git
cd $HOME/Automappa
```

#### First create environment

```bash
make create_environment
```

#### Activate environment

```bash
source activate automappa
```

#### The following will install the automappa entrypoint

```bash
make install
```

Now that all of the dependencies are installed, you may run the app on your local machine or on a server.


### Listing available `make` commands

You may also list other available make commands by simply typing `make` with no other arguments.

```bash
make
```

A few examples:

#### pull docker image

```bash
make docker
```

#### build docker image

```bash
make image
```

## Usage

Simply provide the `automappa` entrypoint with the main binning file output by Autometa as well as the respective markers file.

```bash
automappa \
    --binning-main <path to binning.main.tsv> \
    --markers <path to binning.markers.tsv>
```

----------------------------------------------------------------------------------------------------

## Advanced Usage

### Full `docker run` command example

```bash
# Set automappa parameters (required)
binning="$HOME/test/binning.main.tsv"
markers="$HOME/test/binning.markers.tsv"

# Set docker image/container parameters (optional)
localport=8050
containerport=8886
imagetag="latest"

#NOTE: Some necessary path handling here for binding docker volumes
binning_dirname="$( cd -- "$(dirname "$binning")" >/dev/null 2>&1 ; pwd -P )"
binning_filename=$(basename $binning)
markers_dirname="$( cd -- "$(dirname "$markers")" >/dev/null 2>&1 ; pwd -P )"
markers_filename=$(basename $markers)

# Run with provided parameters
docker run \
    --publish $localport:$containerport \
    --detach=false \
    -v $binning_dirname:/binning:rw \
    -v $markers_dirname:/markers:ro \
    --rm \
    evanrees/automappa:$imagetag \
      --binning-main /binning/$binning_filename \
      --markers /markers/$markers_filename \
      --port $containerport \
      --host 0.0.0.0
```

## Using a remote Automappa server

If you'd like to run Automappa on a *remote* server but view the output on your *local* machine,

### Example remote server login with ssh tunnel

you first need to login to the remote server with a tunnel, e.g. `ssh -L localport:localhost:serverport user@hostaddress`.

```bash
#ssh -L localport:127.0.0.1:serverport user@kwan-bioinformatics.pharmacy.wisc.edu
#example
ssh -L 8888:127.0.0.1:8050 sam@kwan-bioinformatics.pharmacy.wisc.edu
```

Once you are on the server, simply start the Automappa server (with the appropriate port from the ssh tunnel).

```bash
automappa \
    --binning-main <path to binning.main.tsv> \
    --markers <path to binning.markers.tsv> \
    --port 8050
```

Navigate to the app view in your browser.

This will correspond to the localport that was passed in upon login to the remote server.
In the previous example above we would navigate to `localhost:8888`.

I've numbered the ports here to help illustrate the network communication.

| Bridge | Port Bridge | Communication Context |
| :------------- | :------------- | :------------- |
| `localport:remoteport` | `8888:8050` | `local:remote` |

### Using a remote docker container Automappa server

To access Automappa through a docker container that is on a remote machine, one additional bridge
must be constructed.

First we need to forward a port from the server back to our local machine.

```bash
#ssh -L localport:localhost:serverport user@kwan-bioinformatics.pharmacy.wisc.edu
ssh -L 8888:localhost:8887 sam@kwan-bioinformatics.pharmacy.wisc.edu
```

Now run automappa using the docker wrapper script: `run_automappa.sh`

> NOTE: A wrapper is available for download to run docker with port-forwarding.

```bash
curl -o $HOME/run_automappa.sh https://raw.githubusercontent.com/WiscEvan/Automappa/main/docker/run_automappa.sh
chmod a+x $HOME/run_automappa.sh
```

Now start automappa while setting `--localport` to match the `serverport` (`8887` from above).

```bash
# NOTE: This will pull the automappa docker image if it is not already available.
$HOME/run_automappa.sh \
    --imagetag main \
    # NOTE: The 'localport' here is referring to the port on the remote
    --localport 8887 \
    --containerport 8050 \
    --binning binning.main.tsv \
    --markers binning.markers.tsv
```

Now navigate to `http://localhost:8888` and you will see the loaded data.

I've numbered the ports here to help illustrate the network communication.

#### Example port forwarding breakdown

| Server | Port |
| :------------- | :------------- |
| Docker container | 8050 |
| Remote Server | 8887 |
| Local Computer | 8888 |

#### Note

- You may change **any** of these values as long as you change the respective value.
- This will be most useful if **multiple users** will need to use the app.

| Bridge | Port Bridge | Communication Context |
| :------------- | :------------- | :------------- |
| `remoteport:containerport` | `8887:8050` | `remote:docker` |
| `localport:remoteport` | `8888:8887` | `local:remote` |

e.g.

- `localhost:8888` <-> `8888:8887` <-> `8887:8050`

or

- `localhost:localport` <-> `localport:serverport` <-> `serverport:containerport`
