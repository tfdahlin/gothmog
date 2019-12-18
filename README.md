# Gothmog
Gothmog is a package consisting of Python and Node.js applications for deploying a simple botnet.

### Architecture
Gothmog consists of three components:
- A Python server that manages the clients through a unified json API.
- A Python client that connects to the server to receive and execute commands.
- A Node.js server that provides a simple interface for interacting with the server.

### Requirements
The Python API and client are built using Python 3, and have distinct requirements.txt files in their respective folders. Each folder has a `setup.sh` file that can be run to automatically create a virtual environment, and install their required packages. If you don't want a virtual environment, have problems with the installation, or simply want to install the packages yourself, you can navigate to the folder of the component you want to install, then run `pip install -r requirements.txt`.

The web UI is built with Node.js, and can be installed using `npm install` in the `web` folder of the repository. This should take care of installing all necessary dependencies.

### Initial setup
After installation, there are some things that may need to be adjusted for your local environment. 

In the `client` folder, you may want to customize the log file used by the client. By default, logs are stored in a file called `app.log` in the same directory as the client code. This can be changed in the `config.py` file in the client folder.

In the `server` folder, you can similarly change where server logs are output. Additionally, the server has some built-in access control for certain functionality, such as issuing new commands to the clients. By default, it allows the following local address ranges:
- 127.0.0.0/8
- 10.0.0.0/8
- 172.16.0.0/12
- 192.168.0.0/16

These values can be removed if necessary by editing the `__init__` function in the HostDict class. If you want to add additional allowed ip addresses, you can create a file called `allowed_addresses.txt` in the `server` folder, and write additional host subnets for the server to load. These should be in the form of `X.X.X.X/X`. If you did not run the `setup.sh` script in the server folder, you will additionally need to make the server/apps/files/uploaded_files directory, as this is where the server saves uploaded files to.

In the `web` folder, you will need to make some changes to the `settings` object in `settings.js`. If the `site_url` is not changed, the web UI simply will not work correctly. This value should reflect the full address where the web UI is hosted, e.g. `http://127.0.0.1`. This value is what is used in the template for rendering links on the webpage. You can optionally enable TLS by changing `https` to `true`, and changing the value of each `ssl_*` variable to the appropriate path. The `api_url` is used for templating the web UI to point to the appropriate address. If `api_url` is not set, it will default to the same address as the API, but on port 8080.

### Running
Before attempting to run each component, please be sure you have at least read through the `Initial Setup` section to ensure that you do not run into any problems.

##### Client
Launching the client locally is simple, simply activate your virtual environment as necessary, then run `python main.py <api_url> <op_name>`. The `api_url` should include the appropriate protocol and port as necessary, e.g. `http://127.0.0.1:8080`. The `op_name` can be any string that contains only alphanumeric characters, dashes, and underscores. This allows a single API server to run multiple concurrent ops for different users. 

If the client is launched using Docker, it expects environment variables `API_URL` and `OP_NAME`, otherwise it will default to the host machine on port 8080, and `default_op` respectively for these values.

##### API Server
The API server uses waitress to serve the application, and `server.sh` will launch this for you. Waitress by itself doesn't support HTTPS, so if you want to encrypt the traffic, you will have to set it up behind a reverse proxy. By default, the `server.sh` script will launch the API on port 8080, but this can be changed by passing it the `-p` or `--port` argument, e.g. `./server.sh -p 9090`. When run with docker, this runs on port 8080 in the container. If you are using docker-compose, you can use the environment variable `API_PORT` to choose what port is forwarded to port 8080 on the container. If you are not using docker-compose, you can simply specify which port will be forwarded yourself, just make sure it is being forwarded to port 8080 on the container.

##### Web UI Server
The web UI is also easy to launch, simply enter the `web` folder and run `node app.js` to launch. By default, the web server runs on port 80, but this is changed in the `settings.js` file, not by passing arguments at runtime. When run with docker, it instead runs on port 8080 in the container. If you are using docker-compose, you can use the environment variable `WEB_PORT` to choose what port is forwarded to port 8080 on the container. If you are not using docker-compose, you can simply specify which port will be forwarded yourself, just make sure it is being forwarded to port 8080 on the container.

### Disclaimer
This code is _**not**_ designed to be used for unauthorized activity, it is intended to be used as a testing tool in environments where you are authorized to do so. It may be useful for simulating network load, small-scale stress testing, multi-device orchestration, or automation activities. Quite frankly, if you're hoping to deploy this to perform a DDoS, you'd be better off finding something else because deploying this at scale may be costly. 
