# import the lnd_grpc module
import lnd_grpc

# instantiate a new gRPC client object
lnd = lnd_grpc.Client(network='testnet')

# create a random wallet seed
# required to start things on lnd backend
seed = lnd.gen_seed()

# commit the seed and create the new wallet
lnd.init_wallet(wallet_password='password1', cipher_seed_mnemonic=seed.cipher_seed_mnemonic)

# check that the Lightning Servicer is running and we can connect to it
lnd.get_info()
lnd.wallet_balance()

# get a new testnet p2wkh address to receive some coins to
lnd.new_address('p2wkh')

# connect (but not open channel) to a new peer
lnd.connect(address="pubkey@host:port")

# Open a channel with a peer
print(lnd.open_channel_sync(node_pubkey_string=pubkey,
                            local_funding_amount=amt,
                            push_sat=(amt / 2),
                            spend_unconfirmed=True))


###########
# Helpers #
###########

# get ip address
import socket
socket.gethostbyname(socket.gethostname())
