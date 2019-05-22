# Training Outline

### 1. Setup dev environment
Dev environment should be one of:

* Running LND in testnet mode on own machine, requires:
    * Python >=3.6
    * Code editor
* Running LND on Kubernetes cluster and programming using JupyterLab

#### Own machine
* Setup and activate a Python >=3.6 virtual environment
* Download lnd v0.6.1-beta binary for your OS:

    `https://github.com/lightningnetwork/lnd/releases/tag/v0.6.1-beta`
    
* Extract the binary from tar in home directory:

    `tar -C ~/ -xzf lnd-linux-amd64-v0.6.1-beta.tar.gz`
    
* Remove the tar.gz:

    `rm lnd-linux-amd64-v0.6.1-beta.tar.gz`

#### Kubernetes cloud
* To connect to Kubernetes cloud JupyterLab visit:

    `http://35.246.47.214`
    
  and sign in using your GitHub ID via the GitHub OAuth.

----

### 2. Start LND
* Using the terminal, change directory to the extracted lnd beta:

    `cd ~/lnd-linux-amd64-v0.6.1-beta`
    
* Run LND using Neutrino in testnet mode with the following command:

    ```
    ./lnd \
    --bitcoin.active \
    --bitcoin.testnet \
    --debuglevel=info \
    --bitcoin.node=neutrino \
    --neutrino.connect=faucet.lightning.community
    ```

This will connect to Lightning Labs' neutrino node so no local bitcoind is necessary.

This window must be left running (it can run in a screen/tmux session if you so choose), so further terminal commands should be run in a new terminal.

----

### 3. Install lnd_grpc and qrcode
* In a **new** terminal window:

    `pip install lnd_grpc`
* Then:

    `pip install qrcode[pil]`

----

### 4. Initialise the rpc connection
* Import the package using: 

    `import lnd_grpc`
* Create a new client object: 

    `lnd = lnd_grpc.Client(network='testnet')`

----

### 5. Initialise LND with a new wallet via WalletUnlocker Service
To initialise a new LND wallet you must first provide or generate a seed:

`seed = lnd.gen_seed()`

Next you can initialise the wallet which also creates the wallet macaroons:

`lnd.init_wallet(wallet_password='password', cipher_seed_mnemonic=seed.cipher_seed_mnemonic)`

----

### 6. Check the connection to Lightning Service
* check `lnd.get_info()` returns the node info

* check `lnd.wallet_balance()` returns empty sucessfully

----

### 7. Get testnet Bitcoins
* First generate a wallet address to recieve:

    `addr = lnd.new_address('p2wkh')`

* Get some testnet bitcoin:

    * `import qrcode`

    * `from IPython.display import display`

    * `qr_code = qrcode.make(addr.address)`

    * `display(qr_code)`
    
* Wait for confirmations

----

### 8. 