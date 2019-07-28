# Autometa App

## An interactive interface for exploration of highly complex metagenomes.

___

## Feature Requests, Issues, Bugs

I've integrated [Trello boards](https://trello.com/b/8LClJVKA "Link to Autometa-App Trello Board") into the bitbucket repository for noting any feature requests or bugs.

___

## Usage:

### Remote & Docker:

Perhaps the easiest method to start exploring your data will be to run the app from docker image I have made available. This will allow you to skip worrying about the app dependencies and installation and to focus on simply understanding the binning summary provided by AutoMeta.

If you'd like to run the app on the server but view the output on your local machine, you first need to login to the server with a tunnel.

```bash
#ssh -L localport:localhost:serverport user@kwan-bioinformatics.pharmacy.wisc.edu
ssh -L 8888:localhost:8887 jkwan@kwan-bioinformatics.pharmacy.wisc.edu

docker run \
  # Removes the container once you've exited with 'control+C'
  --rm \
  # Data directory to mount inside container
  -v </path/to/data/dir>:/data \
  # Here we are forwarding the port exposed by the container to the host machine
  -p 8887:8886
  # run container from image
  evanrees/autometa-app:latest \
    # autometa-app command:
    index.py \
    --input data/</path/to/autometa/output/file> \
    # Specify the port the container will expose
    --port 8886 \
    #default host name... Should be resolved later for security
    --host 0.0.0.0
```

Navigate to `localhost:8888` and you will see the loaded data.

I've numbered the ports here to help illustrate the network communication.

#### Example port forwarding breakdown
| Server | Port |
| :------------- | :------------- |
| Docker container | 8886 |
| Remote Server | 8887 |
| Local Computer | 8888 |

#### Note:
- You may change **any** of these values as long as you change the respective value.
- This will be most useful if **multiple users** will need to use the app.

| Bridge | Port Bridge | Communiation Context |
| :------------- | :------------- | :------------- |
| remote_server_port:container_port | 8887:8886 | bioinformatics/CHTC server & docker |
| localhost_port:remote_server_port | 8888:8887 | local machine & bioinformatics/CHTC server |

### Local Usage:

Right now the autometa-app requires specific python libraries with specific versions of these libraries. There is a `requirements.txt` file within the repo that should be used to make sure the appropriate dependencies are satisfied.

You can install all of these requirements with `pip`:

- `pip install -r requirements.txt`

Now that all of the dependencies are installed, you may run the app on your local machine or on a server.

### Remote:

If you'd like to run the app on the server but view the output on your local machine, you first need to login to the server with a tunnel.

```bash
#ssh -L localport:127.0.0.1:serverport user@kwan-bioinformatics.pharmacy.wisc.edu
#example
ssh -L 6920:127.0.0.1:8050 jkwan@kwan-bioinformatics.pharmacy.wisc.edu
```

Now once you're on the server, navigate to your autometa-app repository and start the autometa-app server.

```bash
cd </path/to/autometa-app> && python index.py -i </path/to/autometa_output.tsv>
```

Navigate to the app view in your browser. This will correspond to the localport that was passed in upon login to the remote server. In the previous example above we would navigate to `localhost:6920`.

### Navigation and Functionality Display

![dashboard](images/autometaDashboard.gif "Autometa Dashboard")
