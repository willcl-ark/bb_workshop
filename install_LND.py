import os
import tarfile
import urllib.request

url = 'https://github.com/lightningnetwork/lnd/releases/download/v0.6.1-beta/lnd-linux-amd64-v0.6.1-beta.tar.gz'
file_name = "lnd-linux-amd64-v0.6.1-beta.tar.gz"


def run():
    urllib.request.urlretrieve(url, file_name)

    tar = tarfile.open(file_name, "r:gz")
    tar.extractall()
    tar.close()

    if os.path.exists(file_name):
        os.remove(file_name)
    else:
        pass


if __name__ == '__main__':
    run()
