import sys
from shlex import split as shlex_split
from inspect import signature
from pathlib import Path
from functools import wraps
from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.styles import Style
from rich.console import Console


""" A Command-Line Interface """
class CLI:
    def __init__(self):
        self.console = Console()
        self.directory = Path(__file__).resolve().parent
    
    def _run(self):
        """Starts the CLI event loop."""
        self.clear()
        self.draw_logo()

        try:
            while True:
                master_input = prompt("\n> ", completer=self._get_commands_completer()).strip()
                if not master_input:
                    continue

                parts = shlex_split(master_input)
                command, *args = parts

                if command.startswith("_"):
                    self.console.print(f"[red]Unknown command '{command}'. See 'help' for more information.[/red]")
                    continue

                if hasattr(self, command) and callable(getattr(self, command)):
                    method = getattr(self, command)

                    # Preserve function metadata
                    @wraps(method)
                    def safe_call(*args):
                        try:
                            method(*args[: len(signature(method).parameters)])
                        except Exception as e:
                            self.console.print(f"[red]Error: {e}[/red]")

                    safe_call(*args)
                else:
                    self.console.print(f"[red]Unknown command '{command}'. See 'help' for more information.[/red]")

        except KeyboardInterrupt:
            self.console.print("\n[cyan]Terminating CLI instance...[/cyan]")
            sys.exit(0)

    def exit(self):
        """Exits the CLI."""
        sys.exit(0)

    def clear(self):
        """Clears the console screen."""
        self.console.clear()

    def help(self):
        """Displays help text from a file."""
        help_file = self.directory / "resources/help.txt"
        if help_file.exists():
            self.console.print(help_file.read_text())
        else:
            self.console.print("[red]FATAL. Help file not found.[/red]")
    
    def draw_logo(self):
        """Displays the intro message."""
        intro_file = self.directory / "resources/logo.txt"
        if intro_file.exists():
            self.console.print(f"[gold3]{intro_file.read_text(encoding='utf-8')}")

    def _get_commands_completer(self) -> NestedCompleter:
        """Returns the auto-completion for known commands."""
        known_arguments = {
            "help": None,
            "version": {"-v", "--verbose"},
        }

        commands = {
            method: known_arguments.get(method, None)
            for method in dir(self)
            if callable(getattr(self, method)) and not method.startswith("_")
        }

        return NestedCompleter.from_nested_dict(commands)
