import re
class Parser:
    """
    Mainly made for managing commands sintax
    """
    def parse(self, line):
        """
        Validates if the typed line is a valid command
        """
        zero_args_commands = r"(help|list||quit)"
        one_arg_commands = r"(content|create|drop)"
        two_args_commands = r"(delete|down|up)"
        valid_line = rf"({zero_args_commands}|{one_arg_commands}(\s+\w+)|{two_args_commands}(\s+\w+)(\s+\S+$))"
        return True if re.fullmatch(valid_line, line) else False

    def instruction(self, line):
        """
        Returns the command field.
        This should be called only when the command is already parsed.
        """
        return line.split()[0]

    def args(self, line):
        """
        Returns the command args into a tuple.
        This should be called only when the command is already parsed.
        """
        args = tuple(line.split())
        return args[1:] if len(args) > 1 else ()
