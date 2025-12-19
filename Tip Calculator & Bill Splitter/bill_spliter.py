import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

MONEY_PLACES = Decimal(("0.01"))

# Convert to decimal
def to_decimal (text:str) -> Decimal:
    cleaned = text.strip().replace(",","")
    if cleaned == "":
        raise InvalidOperation("Empty input")
    return Decimal(cleaned)

#Round to 2 decimal places using typical financial rounding.
def money(d:Decimal) -> Decimal:
    return d.quantize(MONEY_PLACES,rounding=ROUND_HALF_UP)

