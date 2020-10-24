import socket
from multiprocessing import Process
import os
import sys

class Server:
    """
    This class will represent a Server entity which allows access to remote 
    buckets.
    """
    def __init__(self, root_directory, address = None, port = 9000):
        if not os.path.isdir(root_directory):
            raise ValueError(f"Parameter {root_directory} is not an existing path")
        self.root = root_directory

        self.BUFFER_SIZE = 4096
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #http_bind_address 
        address = socket.gethostname() if address == None else address #set default address it's not given
        try:
            bind_address = (address, port)
            self.socket.bind(bind_address)
        except OSError as e:
            print(f"# Bind failed: {e}")
            sys.exit(1)

    def start(self):
        # become a server socket
        self.socket.listen(10)
        print('# Socket listening')

        while True:
            try:
                # accept connections from outside
                client, address = self.socket.accept()
                # Start a session with the client
                # in this case, we'll pretend this is a processed server
                process = Process(target=self.__session, args=(client, address))
                process.start()
                process.join()
            except KeyboardInterrupt:
                print("\n# Closing connection")
                self.socket.close()
                sys.exit(0)
    
    def __session(self, client, address):   
        print(f"# Connected: {address}")
        while True:
            data = client.recv(self.BUFFER_SIZE)
            if data:
                line = data.decode('UTF-8')    # convert to string (Python 3 only)
                line = line.replace("\n","")   # remove newline character
                print(f"< {address}: {line}")
                client.send((f"Server received: {line}").encode())
            else:
                print(f"# Disconnected: {address}")
                break

if __name__ == "__main__":
    server = Server("buckets/")
    server.start()