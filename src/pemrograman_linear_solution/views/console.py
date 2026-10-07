from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class ConsoleView:
    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def begin_screen(self, title: str, subtitle: str = "") -> None:
        self.console.clear()
        body = Text()
        body.append("PEMROGRAMAN LINEAR SOLUTION", style="bold bright_cyan")
        body.append("\nDEVELOPER: ALFANDOXEON", style="dim")
        if subtitle:
            body.append(f"\n{subtitle.upper()}", style="bright_white")
        self.console.print(Panel(body, title=f"[bold]{title.upper()}[/bold]", expand=True))
        self.console.print()

    def footer(self, text: str = "ALFANDOXEON  |  LINEAR PROGRAMMING COURSEWORK") -> None:
        self.console.print()
        self.console.rule(f"[dim]{text.upper()}[/dim]")

    def message(self, text: str, style: str = "white") -> None:
        self.console.print(text.upper(), style=style)
