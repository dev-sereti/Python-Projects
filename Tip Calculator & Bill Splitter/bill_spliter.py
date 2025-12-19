import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

MONEY_PLACES = Decimal("0.01")

def to_decimal(text: str) -> Decimal:
    # Convert user text to Decimal safely.
    cleaned = text.strip().replace(",", "")
    if cleaned == "":
        raise InvalidOperation("Empty input")
    return Decimal(cleaned)

def money(amount: Decimal) -> Decimal:
    """Round to 2 decimal places using typical financial rounding."""
    return amount.quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)

class TipSplitterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tip Calculator + Bill Splitter")
        self.resizable(False, True)
        self._build_ui()

    def _build_ui(self):
        pad = 10
        main = ttk.Frame(self, padding=pad)
        main.grid(row=0, column=0, sticky="nsew")

        #Inputs
        ttk.Label(main,text="Bill Amount :").grid(row=0,column=0,sticky="w")
        self.bill_var = tk.StringVar(value="0.00")
