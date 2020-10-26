from io import StringIO, BytesIO
from util.parser import Parser
import os
import os.path as path
import shutil
class CommandHandler:
    """
    This class implements actions for every command sent to the Server socket
    """
    def __init__(self, directory):
        this = path.relpath(__file__) # this files path
        root = path.split(this)[0] # removing <filename>.py
        root = path.join(root, directory)
        if not path.isdir(root):
            print(f"# '{root}' is not found. Creating...")
            os.mkdir(root)
        self.root = root
        self.parser = Parser()
    
    def execute(self, line):
        """
        Maps the incoming command to its proper instruction and executes it
        """
        command = self.parser.instruction(line)
        args = self.parser.args(line)
        response = ""
        if command == "content":
            response = self.__content(args[0])
        elif command == "create":
            response = self.__create(args[0])
        elif command == "drop":
            response = self.__drop(args[0])
        elif command == "delete":
            response = self.__delete(args[0], args[1])
        elif command == "list":
            response = self.__list()
        return response

    def __content(self, bucket_name):
        """
        Lists the diferent available buckets
        """
        bucket_path = path.join(self.root, bucket_name)
        if path.isdir(bucket_path):
            files = os.listdir(bucket_path)
            ios = StringIO()
            ios.write(f"Existing files into '{bucket_name}':\n")
            [print(f"    -> {i}", file=ios) for i in files]
            return ios.getvalue()
        return f"Not found: {bucket_name}"

    def __create(self, bucket_name):
        """
        Creates a new bucket into the root directory
        """
        bucket_path = path.join(self.root, bucket_name)
        if not path.isdir(bucket_path):
            os.mkdir(bucket_path)
            return "Success!"
        return "Already exists. Dismissing..."

    def __delete(self, bucket_name, file_name):
        """
        deletes a file from a bucket if exists
        """
        bucket_path = path.join(self.root, bucket_name)
        if path.isdir(bucket_path):
            file_name = path.basename(file_name) #avoids going to any other dirs
            file_path = path.join(bucket_path, file_name)
            if path.isfile(file_path):
                os.remove(file_path)
                return "Success!"
            return f"Not found: {file_name}"
        return f"Not found: {bucket_name}"

    def __drop(self, bucket_name):
        """
        Removes a bucket and its content
        """
        bucket_path = path.join(self.root, bucket_name)
        if path.isdir(bucket_path):
            shutil.rmtree(bucket_path)
            return "Success!"
        return f"Not found: {bucket_name}"

    def __list(self):
        """
        Lists the diferent available buckets
        """
        buckets = os.listdir(self.root)
        ios = StringIO()
        ios.write("Existing buckets:\n")
        [print(f"    -> {i}", file=ios) for i in buckets]
        return ios.getvalue()
    
    def down(self, bucket_name, file_name):
        """
        Looks for a file and loads it into a BytesIO stream ready to be sent.
        """
        bucket_path = path.join(self.root, bucket_name)
        if path.isdir(bucket_path):
            file_name = path.basename(file_name) #avoids going to any other dirs
            file_path = path.join(bucket_path, file_name)
            if path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
            return False
        return False
    
    def up(self, bucket_name, file_name, incoming_bytes):
        """
        Saves the given data into the given metadata (bucket_name, file_name)
        """
        bucket_path = path.join(self.root, bucket_name)
        if path.isdir(bucket_path):
            name = path.join(bucket_path, file_name)
            with open(name, 'wb') as f:
                f.write(incoming_bytes.getvalue())
            return "Success!"
        return f"Not found: {bucket_name}"