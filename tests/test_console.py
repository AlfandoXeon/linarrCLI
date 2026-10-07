import io
import unittest
from unittest.mock import patch

from rich.console import Console

from pemrograman_linear_solution.views.console import ConsoleView


class ConsoleViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.output = io.StringIO()
        self.console = Console(file=self.output, force_terminal=True, color_system=None)
        self.view = ConsoleView(console=self.console)

    @patch("os.system")
    def test_clear_screen_calls_os_system(self, mock_os_system) -> None:
        self.view.clear_screen()
        mock_os_system.assert_called_once()

    @patch("os.system")
    def test_begin_screen_clears_and_renders(self, mock_os_system) -> None:
        self.view.begin_screen("TEST TITLE", "TEST SUBTITLE")
        mock_os_system.assert_called_once()
        rendered = self.output.getvalue()
        self.assertIn("TEST TITLE", rendered)
        self.assertIn("TEST SUBTITLE", rendered)

    def test_no_emojis_in_rendered_components(self) -> None:
        self.view.begin_screen("TITLE")
        self.view.footer(status="TEST STATUS")
        self.view.alert("info", "ALERT TITLE", "ALERT TEXT")
        self.view.card("CARD TITLE", "CARD CONTENT")

        rendered = self.output.getvalue()
        for ch in rendered:
            cp = ord(ch)
            self.assertFalse(0x1F000 <= cp <= 0x1FAFF, f"Found emoji: {ch} ({hex(cp)})")
            self.assertFalse(0x2600 <= cp <= 0x27BF, f"Found symbol: {ch} ({hex(cp)})")


if __name__ == "__main__":
    unittest.main()
