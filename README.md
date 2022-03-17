Automappa
=========

| Image Name           | Image Tag       | Status                                                                                                                                                                                                                |
|----------------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `evanrees/automappa` | `main`,`latest` | [![docker CI/CD](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml/badge.svg?branch=main)](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml)                                       |
| `evanrees/automappa` | `develop`       | [![develop docker CI/CD](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml/badge.svg?branch=develop "evanrees/automappa:develop")](https://github.com/WiscEvan/Automappa/actions/workflows/docker.yml) |

An interactive interface for exploration of highly complex metagenomes
----------------------------------------------------------------------

![automappa_demo_920](https://user-images.githubusercontent.com/25933122/158899748-bf21c1fc-6f67-4fd8-af89-4e732fa2edcd.gif)


## Quickstart using Docker (No installation required):

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
#### Start automappa docker container

```bash
# NOTE: This will pull the automappa docker image if it is not already available.
./run_automappa.sh --imagetag develop \
  --binning binning.main.tsv \
  --markers binning.markers.tsv
```

### Full `docker run` command example

```bash
# Set automappa parameters (required)
binning="$HOME/test/binning.main.tsv"
markers="$HOME/test/binning.markers.tsv"

# Set docker image/container parameters (optional)
localport=8050
containerport=8886
imagetag="develop"

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

----------------------------------------------------------------------------------------------------

## Installation

You can install all of Automappa's dependencies using the Makefile found within the repository.

```bash
cd $HOME
git clone https://github.com/WiscEvan/Automappa.git
cd $HOME/Automappa

# List available commands
make
# pull docker image
make docker
```

### Quickstart from source

```bash
# First create environment
make create_environment
# Activate environment
source activate automappa
# The following will install dependencies and download test data then start automappa
make install_autometa
```

Now that all of the dependencies are installed, you may run the app on your local machine or on a server.

## Usage:

### Local Usage:

```bash
cd $HOME/Automappa
python index.py --binning-main <path to binning.main.tsv> --markers <path to binning.markers.tsv>
```

### Remote using remote install

If you'd like to run the app on the server but view the output on your local machine, 
you first need to login to the server with a tunnel (`ssh -L localport:localhost:serverport user@hostaddress`).

```bash
#ssh -L localport:127.0.0.1:serverport user@kwan-bioinformatics.pharmacy.wisc.edu
#example
ssh -L 8888:127.0.0.1:8050 sam@kwan-bioinformatics.pharmacy.wisc.edu
```

Now once you're on the server, navigate to your Automappa repository and start the Automappa server.

```bash
cd $HOME/Automappa && python index.py \
    --binning-main <path to binning.main.tsv> \
    --markers <path to binning.markers.tsv> \
    --port 8050
```

Navigate to the app view in your browser. 
This will correspond to the localport that was passed in upon login to the remote server. 
In the previous example above we would navigate to `localhost:8888`.

#### Remote using Docker

To access Automappa through a docker container that is on a remote machine, one additional bridge
must be constructed. 

1. We first need to forward a port from the server back to our local machine.

```bash
#ssh -L localport:localhost:serverport user@kwan-bioinformatics.pharmacy.wisc.edu
ssh -L 8888:localhost:8887 sam@kwan-bioinformatics.pharmacy.wisc.edu
```

2. run automappa using the docker wrapper script: `run_automappa.sh`

A wrapper is available for download to run docker with port-forwarding.

```bash
curl -o $HOME/run_automappa.sh https://raw.githubusercontent.com/WiscEvan/Automappa/main/docker/run_automappa.sh
chmod a+x $HOME/run_automappa.sh
```

Now start automappa while setting `--localport` to match the `serverport` (`8887`) from above.

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

#### Note:
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
