import socket
import sys
from util.command import Command

class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #http_bind_address
        self.BUFFER_SIZE = 4096
    
    def run(self):
        self.connect()
        self.__session()

    def connect(self, address = None, port = 9000):
        #set default address it's not given
        address = socket.gethostname() if address == None else address
        print(f"# Connecting to {address}:{port}")
        try:
            self.socket.connect((address, port))
            print("# Connected!")
            self.__session()
        except ConnectionRefusedError:
            print(f"# Connection refused, please make sure there's a server running.")
            sys.exit(1)
        except InterruptedError as e:
            print(f"# Connection interrupted: {e}")
            sys.exit(1)
            
    def __session(self):
        while True:
            try:
                msg = input("> ").strip()
                command = Command(msg)
                if command.validate():
                    self.send(msg)
                else:
                    print(f"# Invalid command: '{msg}', type HELP if you need a hand")
            except KeyboardInterrupt:
                print("\n# Closing connection")
                self.socket.close()
                sys.exit()
            except InterruptedError:
                print(f"# Disconnected from server. :(")
                sys.exit(1)
            """ except:
                print(f"# An error has occured, please try again.")
                sys.exit(1) """

    def send(self, msg):
        self.socket.send(msg.encode())
        data = self.socket.recv(self.BUFFER_SIZE)
        if data:
            line = data.decode('UTF-8')    # convert to string (Python 3 only)
            line = line.replace("\n","")   # remove newline character
            print("< " + line )
        else:
            raise InterruptedError

    """
    def receive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.socket.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)
    """

if __name__ == "__main__":
    client = Client()
    client.run()