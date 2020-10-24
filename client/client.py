from io import StringIO
import socket
import sys
from util.parser import Parser

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
                parser = Parser(msg)
                if msg and parser.parse():
                    self.send(msg)
                else:
                    print(f"# Invalid command: '{msg}', type 'help' if you need a hand")
            except (KeyboardInterrupt, EOFError):
                print("# Disconnected!")
                self.socket.close()
                sys.exit()
            except InterruptedError:
                print(f"# Disconnected due interrupted connection. :(")
                sys.exit(1)

    def send(self, msg):
        if msg == "quit": 
            raise KeyboardInterrupt
        elif msg == "help":
            print(self.__help())
        else:
            self.socket.send(msg.encode())
            data = self.socket.recv(self.BUFFER_SIZE)
            if data:
                line = data.decode('UTF-8')    # convert to string (Python 3 only)
                #line = line.replace("\n","")   # remove newline character
                print("< " + line )
            else: raise InterruptedError

    def __help(self):
        lines = [
            "- content <BUCKET_NAME>: Lists the different files inside the <BUCKET_NAME> bucket.\n",
            "- create <BUCKET_NAME>: Creates a new bucket empty and ready to access. If the bucket is already created, the server will return a reject message.\n",
            "- delete <BUCKET_NAME> <FILE_NAME>: Deletes a file stored inside a bucket.\n",
            "- down <BUCKET_NAME> <FILE_NAME>: Downloads a file from a bucket to the client entity.\n",
            "- drop <BUCKET_NAME>: Deletes an existing bucket.\n",
            "- help: Shows this guideline.\n",
            "- list: Lists the different existing buckets.\n",
            "- quit: Breaks the connection to the server.\n",
            "- up <BUCKET_NAME> <FILE_NAME>: Uploads a file to an existing bucket.\n"
        ]
        ios = StringIO()
        ios.writelines(lines)
        return ios.getvalue()

if __name__ == "__main__":
    client = Client()
    client.run()