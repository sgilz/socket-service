#std lib packages
from io import BytesIO
from multiprocessing import Process
import os
import socket
import sys
#user-defined packages
from command_handler import CommandHandler
from util.parser import Parser
class Server:
    """
    This class will represent a Server entity which allows access to remote 
    buckets.
    """
    def __init__(self, root_directory = "buckets", address = None, port = 9000):
        self.__root_directory = root_directory
        self.BUFFER_SIZE = 1024
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
                self.socket.close()
                sys.exit()
            except:
                print(f"# Disconnected due interrupted connection. :(")
                self.__close_processes(pool, kill=True)
                self.socket.close()
                sys.exit(1)
            finally:
                poolcp = pool.copy()
                for p in poolcp:
                    if not p.is_alive():
                        p.terminate()
                        p.join()
                        pool.remove(p)
    
    def __session(self, client, address):
        print(f"# Connected: {address}")
        while True:
            msg = client.recv(self.BUFFER_SIZE)
            if msg:
                line = msg.decode('UTF-8').replace('\n','')# convert to string (Python 3 only)
                print(f"< {address}: {line}")
                response = self.__response(line, client)
                client.send(response.encode())
            else:
                print(f"# Disconnected: {address}")
                break
        client.close()
    
    def __response(self, line, client):
        """
        Manages incoming lines
        """
        parser = Parser()
        response = ""
        if not parser.parse(line):
            response = f"Command corrupted: {line}"
        else:
            handler = CommandHandler(self.__root_directory)
            instruction = parser.instruction(line)
            if  instruction == "up":
                response = self.__receive_file(client, handler)
            elif instruction == "down":
                response = self.__send_file(line, client, handler)
            else:
                response = handler.execute(line)
        return response
        
    def __receive_file(self, client, handler):
        """
        Receives the file which is in the given path.
        """
        header = client.recv(self.BUFFER_SIZE)
        response = ""
        if header:
            line = header.decode('UTF-8').replace('\n','')
            print(f"< header: {line}")
            client.send("OK".encode()) # sent confirmation of header
            args = line.split()
            if len(args) == 3: 
                bucket_name, file_name, file_size = args
                file_size = int(file_size)
                print(f"# Receiving: {file_name}")
                with BytesIO() as incoming_bytes:
                    total_received = 0
                    while total_received < file_size:
                        bytes_read = client.recv(self.BUFFER_SIZE)
                        total_received += incoming_bytes.write(bytes_read)
                        if not bytes_read:
                            response = "Data corrupted."
                            break
                    print("# Received")
                    response = handler.up(bucket_name, file_name, incoming_bytes)
            else: 
                response = f"Header corrupted: {line}."
        else: 
            response = "Header not found."
        return response

    def __send_file(self, line, client, handler):
        """
        Sends the file which is in the given path.
        """
        response = ""
        bucket_name, file_name = Parser().args(line)
        data = handler.down(bucket_name, file_name)
        if data:
            size = len(data)
            header = f"{bucket_name} {file_name} {size}"
            sent = False
            while not sent: # resending until get confirmation
                client.send(header.encode())
                sent = client.recv(self.BUFFER_SIZE)
            print(f"# Sending {file_name}")
            with BytesIO(data) as buffer:
                while True:
                    bytes_read = buffer.read(self.BUFFER_SIZE)
                    if not bytes_read: 
                            break
                    try:
                        client.sendall(bytes_read)
                    except:
                        print("# Error while sending the file. Please, retry.")
                        return
            print("# Sent")
            client.recv(self.BUFFER_SIZE)
            response = "Success!"
        else:
            client.send("not found".encode())
            response = f"Not found: {bucket_name}/{file_name}"
        return response

    def __close_processes(self, pool, kill = False):
        for p in pool:
            if p.is_alive():
                p.kill() if kill else p.terminate()
                p.join()
        self.socket.close()

def usage():
    return "USAGE:\n    python3 server.py [buckets_root_dir]"

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    if argc == 1:
        server = Server()
        server.start()
    elif argc == 2:
        server = Server(argv[1])
        server.start()
    else:
        print(usage())
    