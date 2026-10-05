"""Serielle Diagnose mit optionaler Spiegelung auf dem OLED."""

from ports.contracts import DiagnosticsPort


class DiagnosticsAdapter(DiagnosticsPort):
    def __init__(self, oled=None):
        self._oled = oled

    def set_oled(self, oled):
        self._oled = oled

    def info(self, message):
        print("INFO:", message)
        self._show("INFO", message)

    def error(self, message):
        print("ERROR:", message)
        self._show("ERROR", message)

    def _show(self, title, message):
        if self._oled is None:
            return
        try:
            self._oled.show_message(title, [str(message)])
        except Exception as exc:
            print("ERROR: OLED diagnostics failed:", exc)


SerialDiagnostics = DiagnosticsAdapter
