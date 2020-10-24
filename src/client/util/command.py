import re
class Command:
    """
    Mainly made for managing 
    """
    def __init__(self, line):
        self.__line = line.strip()

    def validate(self):
        """
        Validates if the typed line is a valid command
        """
        zero_args_commands = r"(HELP|LIST||QUIT)"
        one_arg_commands = r"(CONTENT|CREATE|DROP)(\s+\w+)"
        two_args_commands = r"(DELETE|DOWN|UP)(\s+\w+){2})"
        valid_line = rf"({zero_args_commands}|{one_arg_commands}|{two_args_commands}"
        return True if re.fullmatch(valid_line, self.__line) else False
    
    def instruction(self):
        """
        Returns the command field.
        This should be called just when the command is valid.
        """
        return self.__line.split()[0]

    def args(self):
        """
        Returns the command args into a tuple.
        This should be called just when the command is valid.
        """
        args = tuple(self.__line.split())
        return args[1:] if len(args) > 1 else ()