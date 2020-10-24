from io import StringIO
from util.parser import Parser
import os
import os.path as path
import shutil
class CommandHandler:
    """
    This class implements actions for every command sent to the Server socket
    """
    def __init__(self, directory = "storage"):
        this = path.relpath(__file__) # this files path
        root = path.split(this)[0] # removing <filename>.py
        root = path.join(root, directory)
        if not (path.exists(root) and path.isdir(root)):
            print(f"'{root}' is not an existing directory. Creating...")
            os.mkdir(root)
        self.root = root
    
    def execute(self, line):
        """
        Maps the incoming command to its proper instruction and executes it
        """
        parser = Parser(line)
        if not parser.parse():
            return f"Invalid command: {line}"
        else:
            command = parser.instruction()
            args = parser.args()
            if command == "content":
                return self.__content(args[0])
            elif command == "create":
                return self.__create(args[0])
            elif command == "drop":
                return self.__drop(args[0])
            elif command == "delete":
                return self.__delete(args[0], args[1])
            elif command == "list":
                return self.__list()

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