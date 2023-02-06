from annexremote import Master
from annexremote import SpecialRemote
from annexremote import RemoteError

class CDSRemote(SpecialRemote):
    def initremote(self):
        # initialize the remote, eg. create the folders
        # raise RemoteError if the remote couldn't be initialized
        pass

    def prepare(self):
        # prepare to be used, eg. open TCP connection, authenticate with the server etc.
        # raise RemoteError if not ready to use
        pass

    def transfer_store(self, key, filename):
        # store the file in `filename` to a unique location derived from `key`
        # raise RemoteError if the file couldn't be stored
        pass

    def transfer_retrieve(self, key, filename):
        # get the file identified by `key` and store it to `filename`
        # raise RemoteError if the file couldn't be retrieved
        pass

    def checkpresent(self, key):
        # return True if the key is present in the remote
        # return False if the key is not present
        # raise RemoteError if the presence of the key couldn't be determined, eg. in case of connection error
        pass
        
    def remove(self, key):
        # remove the key from the remote
        # raise RemoteError if it couldn't be removed
        # note that removing a not existing key isn't considered an error
        pass

def main():
    master = Master()
    remote = CDSRemote(master)
    master.LinkRemote(remote)
    master.Listen()

if __name__ == "__main__":
    main()