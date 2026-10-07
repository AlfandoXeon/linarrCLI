import os

from rich import box
from rich.align import Align
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class ConsoleView:
    NAV_ITEMS = [
        ("MENU", "1", "MENU UTAMA"),
        ("BUILDER", "2", "BUAT MODEL"),
        ("PRESETS", "3", "PRESET KASUS"),
        ("GUIDE", "4", "PANDUAN TEORI"),
        ("ABOUT", "5", "TENTANG"),
    ]

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def clear_screen(self) -> None:
        try:
            os.system("cls" if os.name == "nt" else "clear")
        except Exception:
            pass
        self.console.clear()

    def render_navbar(self, active_tab: str = "MENU", breadcrumb: str = "") -> Panel:
        nav_table = Table.grid(expand=True)
        nav_table.add_column("brand", justify="left", ratio=2)
        nav_table.add_column("tabs", justify="right", ratio=3)

        brand_text = Text()
        brand_text.append("PEMROGRAMAN LINEAR SOLUTION", style="bold bright_cyan")
        brand_text.append(" [PRO SUITE v2.0]", style="bold bright_yellow")
        if breadcrumb:
            brand_text.append(f" › {breadcrumb.upper()}", style="dim bright_white")

        tabs_text = Text()
        for tab_id, key, label in self.NAV_ITEMS:
            if tab_id.upper() == active_tab.upper():
                tabs_text.append(f" [{key}] {label} ", style="bold black on bright_cyan")
            else:
                tabs_text.append(f" [{key}] {label} ", style="dim white")
            tabs_text.append(" ")

        nav_table.add_row(brand_text, tabs_text)

        developer_line = Table.grid(expand=True)
        developer_line.add_column(justify="left")
        developer_line.add_column(justify="right")
        developer_line.add_row(
            Text.from_markup("[dim]ENGINE:[/dim] [bold green]TWO-PHASE SIMPLEX[/bold green] [dim]• TOLERANSI: 1e-9[/dim]"),
            Text.from_markup("[dim]DEVELOPER:[/dim] [bold gold1]ALFANDOXEON[/bold gold1] [dim]• GITHUB: ALFANDOXEON[/dim]"),
        )

        content = Table.grid(expand=True)
        content.add_row(nav_table)
        content.add_row(Text("─" * 80, style="dim cyan"))
        content.add_row(developer_line)

        return Panel(
            content,
            box=box.DOUBLE,
            border_style="bright_cyan",
            padding=(0, 1),
        )

    def begin_screen(
        self,
        title: str,
        subtitle: str = "",
        active_tab: str = "MENU",
        breadcrumb: str = "",
    ) -> None:
        self.clear_screen()
        self.console.print(self.render_navbar(active_tab, breadcrumb or title))

        if title:
            screen_title = Text()
            screen_title.append(title.upper(), style="bold white")
            if subtitle:
                screen_title.append(f"  —  {subtitle.upper()}", style="italic cyan")

            banner = Panel(
                Align.center(screen_title),
                box=box.ROUNDED,
                border_style="bright_yellow",
                style="on grey11",
                padding=(0, 1),
            )
            self.console.print(banner)
            self.console.print()

    def footer(
        self,
        text: str = "",
        hints: list[tuple[str, str]] | None = None,
        status: str = "SIAP (READY)",
        status_color: str = "spring_green2",
    ) -> None:
        self.console.print()

        grid = Table.grid(expand=True)
        grid.add_column("hints", justify="left", ratio=3)
        grid.add_column("status", justify="right", ratio=2)

        hints_text = Text()
        if hints:
            for key, desc in hints:
                hints_text.append(f"[{key}]", style="bold black on bright_yellow")
                hints_text.append(f" {desc.upper()}   ", style="bold white")
        elif text:
            hints_text.append("PETUNJUK: ", style="bold bright_cyan")
            hints_text.append(text.upper(), style="bright_white")
        else:
            hints_text.append("[0] KEMBALI / KELUAR   [?] BANTUAN", style="dim white")

        status_text = Text()
        status_text.append("STATUS: ", style="dim")
        status_text.append(f"[{status.upper()}]", style=f"bold {status_color}")
        status_text.append(" │ ALFANDOXEON", style="bold gold1")

        grid.add_row(hints_text, status_text)

        panel = Panel(
            grid,
            box=box.ROUNDED,
            border_style="cyan",
            padding=(0, 1),
        )
        self.console.print(panel)

    def message(self, text: str, style: str = "white") -> None:
        self.console.print(text.upper(), style=style)

    def alert(self, level: str, title: str, text: str) -> None:
        colors = {
            "success": "bright_green",
            "warning": "bright_yellow",
            "error": "bright_red",
            "info": "bright_cyan",
        }
        color = colors.get(level.lower(), "bright_white")
        panel = Panel(
            Text(text.upper(), style="white"),
            title=f"[bold {color}]{title.upper()}[/bold {color}]",
            border_style=color,
            box=box.ROUNDED,
            padding=(0, 1),
        )
        self.console.print(panel)

    def card(
        self,
        title: str,
        content: RenderableType,
        border_style: str = "bright_cyan",
        box_style: box.Box = box.ROUNDED,
    ) -> Panel:
        return Panel(
            content,
            title=f"[bold {border_style}]{title.upper()}[/bold {border_style}]",
            border_style=border_style,
            box=box_style,
            padding=(1, 2),
        )

    def render_kpi_cards(self, cards: list[dict[str, str]]) -> Table:
        grid = Table.grid(expand=True)
        for _ in cards:
            grid.add_column(justify="center", ratio=1)

        panels = []
        for card in cards:
            color = card.get("color", "bright_cyan")
            title = card.get("title", "")
            value = card.get("value", "")
            subtitle = card.get("subtitle", "")

            body = Text()
            body.append(f"\n{value}\n", style=f"bold {color}")
            if subtitle:
                body.append(f"{subtitle.upper()}", style="dim white")

            panels.append(
                Panel(
                    Align.center(body),
                    title=f"[bold {color}]{title.upper()}[/bold {color}]",
                    border_style=color,
                    box=box.ROUNDED,
                    padding=(0, 1),
                )
            )

        grid.add_row(*panels)
        return grid
