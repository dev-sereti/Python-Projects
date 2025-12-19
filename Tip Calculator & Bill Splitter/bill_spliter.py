import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

MONEY_PLACES = Decimal("0.01")

def to_decimal(text: str) -> Decimal:

    # Convert user text to Decimal safely.
    # Allows commas in numbers like '1,234.56'.
   
    cleaned = text.strip().replace(",", "")
    if cleaned == "":
        raise InvalidOperation("Empty input")
    return Decimal(cleaned)

def money(d: Decimal) -> Decimal:
    """Round to 2 decimal places using typical financial rounding."""
    return d.quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)

class TipSplitterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tip Calculator + Bill Splitter")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        pad = 10
        main = ttk.Frame(self, padding=pad)
        main.grid(row=0, column=0, sticky="nsew")