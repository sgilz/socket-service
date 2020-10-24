from command_handler import CommandHandler
from multiprocessing import Process
import os
import socket
import sys

class Server:
    """
    This class will represent a Server entity which allows access to remote 
    buckets.
    """
    def __init__(self, root_directory, address = None, port = 9000):
        self.__root_directory = root_directory
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
        print('# Server listening')
        pool = list()
        while True:
            try:
                # accept connections from outside
                client, address = self.socket.accept()
                # Start a session with the client
                # in this case, we'll pretend this is a processed server
                process = Process(target=self.__session, args=(client, address))
                pool.append(process)
                process.start()
            except KeyboardInterrupt:
                print("\n# Closing connection")
                self.__close_processes(pool, kill=True)
                sys.exit()
            except Exception as e:
                self.__close_processes(pool, kill=True)
                raise e
            finally:
                poolcp = pool.copy()
                for p in poolcp:
                    if not p.is_alive():
                        p.terminate()
                        p.join()
                        pool.remove(p)
    
    def __session(self, client, address):   
        print(f"# Connected: {address}")
        handler = CommandHandler(self.__root_directory)
        while True:
            data = client.recv(self.BUFFER_SIZE)
            if data:
                line = data.decode('UTF-8')    # convert to string (Python 3 only)
                line = line.replace('\n','')   # remove newline character
                print(f"< {address}: {line}")
                response = handler.execute(line)
                client.send(response.encode())
            else:
                print(f"# Disconnected: {address}")
                break

    def __close_processes(self, pool, kill = False):
        for p in pool:
            if p.is_alive():
                p.kill() if kill else p.terminate()
                p.join()
        self.socket.close()

if __name__ == "__main__":
    server = Server("buckets/")
    server.start()