import re
class Parser:
    """
    Mainly made for managing commands sintax
    """
    def __init__(self, line):
        self.__line = line.strip()

    def parse(self):
        """
        Validates if the typed line is a valid command
        """
        zero_args_commands = r"(help|list||quit)"
        one_arg_commands = r"((content|create|drop)(\s+\S+))"
        two_args_commands = r"((delete|down|up)(\s+\S){2})"
        valid_line = rf"({zero_args_commands}|{one_arg_commands}|{two_args_commands})"
        return True if re.fullmatch(valid_line, self.__line) else False

    
    def instruction(self):
        """
        Returns the command field.
        This should be called only when the command is already parsed.
        """
        return self.__line.split()[0]

    def args(self):
        """
        Returns the command args into a tuple.
        This should be called only when the command is already parsed.
        """
        args = tuple(self.__line.split())
        return args[1:] if len(args) > 1 else ()
