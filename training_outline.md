# Training Outline

### 1. Setup dev environment
Dev environment should be one of:

* Running LND in testnet mode on own machine, requires:
    * Python >=3.6
    * Code editor
* Running LND on Kubernetes cluster and programming using JupyterLab

#### Own machine
* Setup and activate a Python >=3.6 virtual environment
* Download lnd v0.6.1-beta binary for your OS: `https://github.com/lightningnetwork/lnd/releases/tag/v0.6.1-beta`
* Extract the binary from tar in home directory: `tar -C ~/ -xzf lnd-linux-amd64-v0.6.1-beta.tar.gz`
* Remove the tar.gz: `rm lnd-linux-amd64-v0.6.1-beta.tar.gz`

#### Kubernetes cloud
* To connect to Kubernetes cloud JupyterLab visit: `http://35.246.47.214` and sign in using your GitHub ID via the GitHub OAuth.

----

### 2. Start LND
* Using the terminal, change directory to the extracted lnd beta: `cd ~/lnd-linux-amd64-v0.6.1-beta`
* Run LND using Neutrino in testnet mode with the following command:
```
./lnd \
--bitcoin.active \
--bitcoin.testnet \
--debuglevel=info \
--bitcoin.node=neutrino \
--neutrino.connect=faucet.lightning.community
```

This will connect to the handy LND neutrino node so no local bitcoind is necessary.

----

### 3. Install lnd_grpc python package
* In a **new** terminal window:
`pip install lnd_grpc`

----

### 4. Initialise the rpc connection
* Import the package using: `import lnd_grpc`
* Create a new client object: `lnd = lnc_grpc.Client(network='testnet')`
