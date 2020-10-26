#std lib packages
from io import StringIO, BytesIO
import os
import os.path as path
import socket
import sys
#user-defined packages
from util.parser import Parser

class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #http_bind_address
        self.BUFFER_SIZE = 1024
        self.parser = Parser()
    
    def run(self, address = None, port = 9000):
        """
        Tries to connect to the server deployed on the given access point (address:port).
        and  start a session with it.
        """
        #set default address if it's not given
        address = socket.gethostname() if address == None else address
        self.__connect( address, port)
        self.__session()

    def __connect(self, address, port):
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
                if msg and self.parser.parse(msg):
                    self.__execute(msg)
                else:
                    print(f"# Invalid command: '{msg}', type 'help' if you need a hand.")
            except (KeyboardInterrupt, EOFError):
                print("# Disconnected!")
                self.socket.close()
                sys.exit()
            except (InterruptedError, ConnectionError):
                print(f"# Disconnected due interrupted connection. :(")
                self.socket.close()
                sys.exit(1)

    def __execute(self, msg):
        instruction = self.parser.instruction(msg)
        if msg == "quit": 
            raise KeyboardInterrupt
        elif msg == "help":
            print(self.__help())
        elif instruction == "up":
            self.__send_file(msg)
        elif instruction == "down":
            self.__receive_file(msg)
        else:
            self.socket.send(msg.encode())
        self.__listen(msg)
    
    def __send_file(self, msg):
        """
        Sends the file which is in the given path.
        """
        self.socket.send(msg.encode()) # advertisement

        bucket_name, file_path = self.parser.args(msg)
        if path.isfile(file_path):
            file_name = path.basename(file_path)
            size = path.getsize(file_path)
            header = f"{bucket_name} {file_name} {size}"
            sent = False
            while not sent: # resending until get confirmation
                self.socket.send(header.encode())
                sent = self.socket.recv(self.BUFFER_SIZE)
            with open(file_path, 'rb') as f:
                print(f"# Sending {file_name}")
                while True:
                    bytes_read = f.read(self.BUFFER_SIZE)
                    if not bytes_read: 
                            break
                    try:
                        self.socket.sendall(bytes_read)
                    except:
                        print("# Error while sending the file. Please, retry.")
                        return
                print("# Sent")
        else:
            print(f"# Not found file: {file_path}")
        
    def __receive_file(self, msg):
        """
        Receives the file which is in the given path.
        """
        self.socket.send(msg.encode())
        header = self.socket.recv(self.BUFFER_SIZE)
        if header:
            line = header.decode('UTF-8').replace('\n','')
            if line == "not found": #  omit transmission if bucket or file doesn't exist
                return 
            self.socket.send("OK".encode()) # sent confirmation of header
            args = line.split()
            if len(args) == 3:
                bucket_name, file_name, file_size = args
                file_size = int(file_size)
                print(f"# Receiving: {file_name}")
                with BytesIO() as incoming_bytes:
                    total_received = 0
                    while total_received < file_size:
                        bytes_read = self.socket.recv(self.BUFFER_SIZE)
                        total_received += incoming_bytes.write(bytes_read)
                        if not bytes_read:
                            print("# Data corrupted. Dismissing...")
                            return
                    print("# Received")
                    self.socket.send("OK".encode()) # sent confirmation of data

                    this = path.relpath(__file__) # this files path
                    this = path.split(this)[0] # removing <filename>.py
                    down_path = path.join(this, "downloads", bucket_name)
                    if not path.isdir(down_path):
                        print(f"# '{down_path}' not found. Creating...")
                        os.makedirs(down_path)
                    file_path = path.join(down_path, file_name)
                    with open(file_path, 'wb') as f:
                        f.write(incoming_bytes.getvalue())
            else:
                print("# Header corrupted.")
        else: 
            print("# Header not found.")

    def __listen(self, msg):
        data = self.socket.recv(self.BUFFER_SIZE)
        if data:
            line = data.decode('UTF-8')    # convert to string (Python 3 only)
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
            "- up <BUCKET_NAME> <FILE_NAME>: Uploads a file to an existing bucket.\n\n",
            "* REMARKS: \n",
            "    - The available commands are all CASE-SENSITIVE\n"
            "    - <BUCKET_NAME> only accepts alphanumeric, numeric and '_' chars.\n",
            "    - <FILE_NAME accepts the same as <BUCKET_NAME> + and optional aphanumeric extension.\n"
        ]
        ios = StringIO()
        ios.writelines(lines)
        return ios.getvalue()

if __name__ == "__main__":
    client = Client()
    client.run()