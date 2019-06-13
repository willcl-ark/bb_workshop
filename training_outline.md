# Training Outline

### 1. Setup dev environment
Dev environment should be one of:

* Running workshop in testnet mode on own machine, requires:
    * Python >=3.6
    * lnd v0.6.1-beta
    * Code editor
    
* Running LND on Kubernetes cluster and programming using JupyterLab, requires:
    * Github account for login

#### Own machine
* Setup and activate a Python >=3.6 virtual environment
* Download lnd v0.6.1-beta binary for your OS: [lnd/releases/v0.6.1-beta](https://github.com/lightningnetwork/lnd/releases/tag/v0.6.1-beta)
    
* Extract the binary, e.g. for linux from tar in home directory:

    ```bash
    tar -C ~/ -xzf lnd-linux-amd64-v0.6.1-beta.tar.gz
    ```
    
* Remove the tar.gz:

    ```bash
    rm lnd-linux-amd64-v0.6.1-beta.tar.gz
    ```

#### Kubernetes cloud
* To connect to Kubernetes cloud JupyterLab visit [Kubernetes Login](http://35.246.47.214)
    
  and sign in using your GitHub ID via the GitHub OAuth.

----

### 2. Start LND
* Using the terminal, change directory to the extracted lnd beta:

    `cd ~/lnd-linux-amd64-v0.6.1-beta`
    
* Run LND using Neutrino in testnet mode with the following command:

    ```bash
    ./lnd --bitcoin.active --bitcoin.testnet --debuglevel=info --bitcoin.node=neutrino --neutrino.addpeer=btcd-testnet.lightning.computer 
    ```
    
This will connect to Lightning Labs' neutrino node so no local bitcoind is necessary. There has been ~1,500,000 blocks on testnet3 now, so inital sync can take some time. Hopefully no longer than 10 minutes with some decent CPU. With debug level set to 'debug' we can keep an eye on progress and turn down the debug level later using the python RPCs.

This window must be left running (it can run in a screen/tmux session if you so choose), so any further terminal commands should be run in a new terminal session.

----

### 3. Install lnd_grpc and qrcode
* In a **new** terminal window, first we update pip:

  ```bash
  pip install --upgrade pip
  ```
 
* Now install LND:

  ```bash
  pip install --user lnd_grpc
  ```
    
* Then:

  ```bash
  pip install --user qrcode[pil]
  ```
  
  We will only use the QR code module to display a receive address to more easily send you testnet coins.
  
* Add the qrcode script path to PATH to satisfy warning:

  ```bash
  PATH=$PATH:/home/jovyan/.local/bin
  ```
  
----

### 4. Initialise the rpc connection
* In a Jupyter Notebook window (if using Kubernetes) or a python REPL console (if using own machine):

* Import the client class from the package: 

    ```python
    from lnd_grpc import Client
    ```
      
* Now we are ready to create a new client object called 'lnd': 

    ```python
    lnd = Client(network='testnet')
    ```  

* Now is a good time to open a tab with all the LND RPC commands for reference:     [lnd-grpc-api-reference](https://api.lightning.community/?python#lnd-grpc-api-reference)
  You can also access the docstring help using standard Python `help(Class.method)` syntax

----

### 5. Initialise LND with a new wallet via WalletUnlocker Service
* To initialise a new LND wallet you must first provide or generate a seed:

    ```python
    seed = lnd.gen_seed()
    ```

* Next you can initialise the wallet which also creates the wallet macaroons:

    ```python
    lnd.init_wallet(wallet_password='password', cipher_seed_mnemonic=seed.cipher_seed_mnemonic)
    ```

----

### 6. Check the connection to Lightning Service
* check `lnd.get_info()` returns the node info

* check `lnd.wallet_balance()` returns empty sucessfully

----

### 7. Get testnet Bitcoins
* First we have to make sure that we are synced to the network fully:

    ```python
    lnd.get_info().synced_to_chain
    ```
    ... should return True
    
    
* If you wanted to be notified when sync is complete, you could wait on the result with something like:

    ```python
    import time
    while not lnd.get_info().synced_to_chain:
        time.sleep(1)
    print('Synced!')
    ```

* Generate a new receive address:

    ```python
    addr = lnd.new_address('p2wkh')
    ```  

* Create a QR code to get some testnet bitcoin:

    ```python
    import qrcode
    from IPython.display import display
    qr_code = qrcode.make(addr.address)
    display(qr_code)
    ```
    
* Wait for confirmations. Unfortunately testnet blocktimes can be between 1 minute and 20 minutes due to its nature, so hopefully we don't have to wait long. You can check whether your coins are confirmed using `lnd.wallet_balance()` which will show it as unconfirmed balance.


----

### 8. Connect to peers
* In the meantime we can connect to some peers. There are two peer connection methods in lnd-grpc, one which is the default lnd RPC command `connect_peer` and one which simplifies address entry, `connect`. connect_peer requires a ln.LightningAddress object as argument, whereas `connect` allows you to pass the address in string format as `"node_pubkey@host:port"`:

    1. `lnd.connect_peer(addr: ln.LightningAddress)` or
    2. `lnd.connect(address)`

* To more easily swap node pubkeys, which you can obtain from `lnd.get_info().identity_pubkey`, perhaps a good idea to paste them into a google document: [node pubkeys](https://docs.google.com/spreadsheets/d/1eXq1bJFH_5I6ID2kpeJBdOkN5RMQCZmIug3GTgN2G6Y/edit#gid=0)

* To get the IP address of workshop peers, open a new terminal (not python) window, and simply type `hostname -i`. This should return the required ip address.

* The default port of 9735 is being used.

* The suggestion would be to use the `connect` command, but you can try either!

    ```python
    lnd.connect(address="node_pubkey@ip_address:port")
    ```
    
* Note that connecting is not the same as opening a channel, it is simply a networking-level connection, but it helps to find peers using ip addresses in case you do not have the full network graph info (or they do not appear in your network graph).

* You can see which peers you are connected to at any time using
    ```python
    lnd.list_peers()
    ```

* It might also be fun to connect to and open a channel to a regular testnet peer too, so that we are not stuck on our own micro-lightning network. Find a peer on [1ml-testnet](https://1ml.com/testnet) to connect to as above.

----

### 9. Open a channel

* Next up is to finally open a channel with a peer. As we are already `connect`-ed to them, we only need to provide the pub_key and local funding amount to start.

* We will start with the synchronous version of open channel, as it blocks while it opens, but then nicely returns the result for us to see.

* As we are using hex-encoded node_pubkeys (as returned by get_info), we must be careful to use the proper argument, `node_pubkey_string` rather than `node_pubkey`:

    ```python
    lnd.open_channel_sync(node_pubkey_string="", local_funding_amount)
    ```
    
* If successful, you will see the funding txid returned

* Try to open a channel with at least one local peer and your 'WAN' peer from 1ML databse.

----

### 10. Create an invoice

* Now we want to make a payment. Although direct 'key_send'/'sphinx send' is technically possible on mainnet today, we will use the standard invoice-payment lightning model

* First, the receiver must create an invoice. This is easily done with `lnd.add_invoice()` which needs no additional parameters, not even a value! However conventionally the receiver requests a 'value' at least. A zero-value invoice can have any amount paid to it otherwise...

    ```python
    invoice = lnd.add_invoice(value=5000)
    invoice
    ```
    
* You can see the r_hash ('payment hash') as raw bytes, and the hex-encoded payment request along with the add_index. As the creator of the invoice, we also know the preimage ('r_preimage) and various other details, which we can expose by looking up the invoice by the payment hash. To avoid bytes conversions and other issues, we will simply reference the `invoice`'s .r_hash attribute in the lookup_invoice() method:

    ```python
    lnd.lookup_invoice(r_hash=invoice.r_hash)
    ```
    
    This will reveal the preimage, which is what we will reveal to the sender, upon receiving their "promise to pay".
    
----

### 11. Pay an invoice

* First we need to share these BOLT11-encoded payment requests. This is ually done via other channels, e.g. through a web interface, as we have none, we can use google docs again: [invoice payment_requests](https://docs.google.com/spreadsheets/d/1eXq1bJFH_5I6ID2kpeJBdOkN5RMQCZmIug3GTgN2G6Y/edit#gid=1809562352)

* Once you have retrieved the payment request of the invoice you wish to pay, and especially for this method we have used of communicating them where there is a good chance they might get mixed up, it is a good idea to decode the payment request and check that it is as you expect.
   
    ```python
    lnd.decode_payment_req(pay_req="payment_request_string")
    ```
    
* The payment request is similarly decoded and checked using the `lncli` workflow

* If the payment request is correct, then we can pay the invoice using `send_payment()` command:

    ```python
    lnd.send_payment_sync(payment_request="payment_request_string")
    ```
    
* If successful, the payment preimage (r_preimage) will be displayed, along with the payment_hash (r_hash) and the route. If it fails, an appropriate error will be returned in full.

----

### 12. Backup

* Now that we have opened some channels, it's the perfect time to back them up. LND has static channel backups (SCB) which, although not perfect, is the best option we have to offer at this stage.

  *** Note that the below is specifically a channel backup and restore process. To backup and restore on-chain funds, only the `cipher_seed_mnemonic`. The `wallet_password` only encrypts this wallet on the disk. ***

* SCB protocol will attempt to recover on-chain and payment channel balances, although only on-chain is fully guaranteed.

* Although LND will create a `channel.backup` file automatically, it might not always be up to date. Make an up-to-date version using:

    ```python
    backup = lnd.export_all_channel_backups()
    ```
  
  *** As we are not writing this backup to disk, only storing as a variable, be sure not to close this Notebook Window if you want to test a full delete and restore! ***
    
* Next it makes sense to verify that the backup will work, which you can do using:

    ```python
    lnd.verify_chan_backup(multi_chan_backup=backup.multi_chan_backup)
    ```
    
* If you want to test the full workflow, you can try to delete the channel database and restore it:

* Stop LND (ctrl+c in its terminal window), and then delete the channel.db using

    ```bash
    rm ~/.lnd/data/graph/testnet/channel.db
    ```
  
* Now you can restart LND in the terminal using the same command used in 2. above. Switch back to the Jupyter Notebook and try to unlock the wallet using the same 'lnd' object -- it should still work even though LND node has been restarted:

    ```python
    lnd.unlock_wallet(wallet_password='password')
    ```
    (or whatever password you chose in 5.)

* If the wallet unlocks, you can check that your previously-opened channels are not lost from the database: 

    ```python
    lnd.list_channels()
    ```
    should return nothing.
    
* Now lets try the restore:

    ```python
    lnd.restore_chan_backup(multi_chan_backup=backup.multi_chan_backup.multi_chan_backup)
    ```
  
  If successful, it will still take a while for LND to recover the funds back into the on-chain wallet. The SCB protocol (more specifically the Data Loss Protection [DLP] protocol) requests that the channel partner force closes the channel. Before they do though, they'll send over the channel reestablishment handshake message which contains the unrevoked commitment point which we need to derive keys (will be fixed in BOLT 1.1 by making the key static) to sweep our funds.
  
* We can observe the log in the terminal session running LND to try and watch for the SCB process to complete. The first step takes around 60 seconds, but after that requires some on-chain confirmations, so total time can vary. A selection of lines to watch for in the log as progress: 

    ```bash
    'Inserting 1 SCB channel shells into DB'
    'Broadcasting force close transaction'
    'Publishing sweep tx'
    '...a contract has been fully resolved!'
    ```
    
* As a result of successful backup restore, all funds will be returned to the on-chain wallet (minus transaction fees), and the channels will be marked as 'recovered' and not allowed to be re-used.

* You can also subscribe to `channel.backup` status changes using `lnd.subscribe_channel_backups()` to stimulate backup process, or write a shell script to manually monitor the `channel.backup` file on the filesystem itself, e.g. [this script](https://gist.github.com/alexbosworth/2c5e185aedbdac45a03655b709e255a3).

  The Raspiblitz project also has a lot of neat shell scripts for things like this.
  
----

### 13. Threading of streaming 'subscription' RPCs

* There are multiple 'subscribe' RPC calls which setup a server-client stream to notify the client of new events. As they are implemented, these will naturally block the single Python GIL thread, so we must setup threads to run these sanely.

  ```python
  import threading
  def sub_invoices():
      for response in lnd.subscribe_invoices():
          print('\n\n-------\n')
          print(f'New invoice from subscription:\n{response}\n\n')
  
  invoice_sub = threading.Thread(target=sub_invoices, daemon=True)
  invoice_sub.start()
  ```
  
* Once the thread has started, you can create a new invoice and watch the subscription detect it.

  Note that due to using REPL/Jupyter Notebook, we will see both the return of `add_invoice()` command, and also the `print()` from our subscription which shows some double information. Usually you would be adding these invoices to a queue or database.

  ```python
  lnd.add_invoice(value=500)
  ```
  
  The same process can be used for `subscribe_transactions()`, `subscribe_channel_events()` and `subscribe_channel_graph()`. The number of threads is limited only by your CPU, but for low computation threads like most of these, the number could be some 000's
  
----

### 14. Hold Invoices

* Quite a complicated workflow, where the main difference from normal invoice process is that the receiver does not have to settle the invoice immediately -- they can 'refuse' the payment.

* This creates some extra requirements on the programming side, as

     i) receiver must monitor for 'payment' of the invoice (before deciding whether to settle),
    
     ii) the sender's `pay_invoice()` command will block indefinitely, until the receiver decides to settle and
    
     iii) the receiver needs to settle when they are happy to do so.

* As we need to generate our own preimage, we need to generate 32 random bytes and also get the sha256 hash digest. Python has a nice library called secrets for generating random bytes:

  **Recipient step:**

  ```python
  from hashlib import sha256
  from secrets import token_bytes

  def random_32_byte_hash():
      """
      Can generate an invoice preimage and corresponding payment hash
      :return: 32 byte sha256 hash digest, 32 byte preimage
      """
      preimage = token_bytes(32)
      _hash = sha256(preimage)
      return _hash.digest(), preimage
  
  # generate a hash and preimage
  _hash, preimage = random_32_byte_hash()
  ```
  
 * The recipient can now generate the hold invoice, manually supplying the sha256 hash we generated as the invoice hash:
 
   **Recipient step:**
 
  ```python
  invoice = lnd.add_hold_invoice(memo='pytest hold invoice', hash=_hash, value=1001)
  ```
  
  As before, we will need to exchange this out of band, so paste the payment request string and some identifier into the google sheet.

* Now we can define the functions we will need to thread:

  **Recipient step:**
  
  ```python
  def inv_sub_worker(_hash):
      for _response in lnd.subscribe_single_invoice(_hash):
          print(f'\n\nInvoice subscription update:\n{_response}\n')
  ```
  
  **Sender step:**
  
  ```python
  def pay_hold_inv_worker(payment_request):
      lnd.pay_invoice(payment_request=payment_request)
  ```
  
* Now we can begin the payment sequence. First the recipient should subscribe to updates for the invoice so they know when they've received payment:

  **Recipient step:**
  
  ```python
  # setup the thread
  inv_sub = threading.Thread(target=inv_sub_worker, name='inv_sub',
                             args=[_hash, ], daemon=True)
  
  # start the subscription thread
  inv_sub.start()
  ```
  
  You can check if the thread has started properly with `inv_sub.is_alive()`
  
* Now the sender can make the payment. As mentioned above, this will block until settled, so its useful to run in a thread too. Retrieve the payment_request string from the google sheet.

  **Sender step:**
  
  ```python
  # setup the pay thread
  pay_inv = threading.Thread(target=pay_hold_inv_worker, args=[payment_request="payment_request", ])
  
  # Start the pay thread
  pay_inv.start()
  ```

* At this stage, the recipient should see the print from their subscription thread that the invoice has had an update. Now the ball is in their court as they can choose to settle or cancel the invoice. Lets look at these two options.

  **Recipient step, option 1 - settle invoice:**
  
  ```python
  # to settle, we can just call settle_invoice() with the preimage
  lnd.settle_invoice(preimage=_preimage)
  ```
  
  **Reciepient step, option 2 - cancel payment:**
  
  ```python
  # to cancel invoice we call cancel_invoice() with the hash of the preimage (payment_hash)
  lnd.cancel_invoice(payment_hash=_hash)
  ```
  
* After settling or canceling, the recipient should receive the appropriate response from their invoice subscription (and possibly the return of the settle/cancel call itself).

* The sender's `pay_inv()` thread will then also return. It will include either a populated `payment_error` field indicating failure, or a populated `payment_preimage` field, indicating the payment was settled successfully. 

----

### Advanced Challenges

#### Route-finding

* See if you can find a route to 03933884aaf1d6b108397e5efe5c86bcf2d8ca8d2f700eda99db9214fc2712b134 for about 3000 satoshis

    * If not, choose a new, well-conneted node from [1ml-testnet](https://1ml.com/testnet), connect the them and open an appropriately-sized channel.
    
    * Try searching for a route again.

* Get a new invoice from this node, hint: the node pubkey is that of [Starblocks](https://starblocks.acinq.co/#/), so visit their website and proceed to buy a coffee.

* When you have your invoice for the coffee, decode the payment request just to double check the node_pubkey is the same (and that they didn't change node pub_key since writing of this guide!)

* Don't just pay the payment request, using the route that you've saved, pay the invoice using `send_to_route()` or `send_to_route_sync()` command.

----

#### Channel balancing:

* Get an invoice which will allow you to deplete a channel and empty it (hint: you must reserve 1% of a channel capacity, so you can never fully deplete)

* Open another channel with 1.5x the capacity of the first, but ensure that it is with a different peer

* Try to find a route from your newly-funded channel, back to yourself at your original empty channel

* Make a payment along the route with a value of 50% the capacity of the original channel. Now you should have two balanced channels

----

#### Bi-directional payment channel sphinx send

* Stop the jupyter notebook kernel (don't need to close the workbook)

* From the terminal, remove current version of lnd-grpc, `pip uninstall --user lnd-grpc`

* Change to the home directory, clone the lnd-grpc source code and enter the directory:

  `cd ~; git clone https://github.com/willcl-ark/lnd_grpc.git; cd lnd_grpc`

* Checkout branch send_payment_sphinx:

  `git checkout send_payment_sphinx`
  
* install this branch as an editable package:

  `pip install -e .`

* This branch includes a change to the asynchronous `send_payment()` method so that it will accept an arbitrary request generator.

* It also expands the SendPayment protocol message to include the `key_send` attribute, which enables you to send to a node's (public) key directly.

* Attempt a sphinx send using the `send_payment(key_send=node_pubkey)` RPC call.

* Create a request generator to use with a sphinx `send_payment` call which will send a payment of 20 satoshis every 20 seconds for 1 minute.

