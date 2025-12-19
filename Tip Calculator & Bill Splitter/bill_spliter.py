import tkinter as tk
from tkinter ttk,messagebox
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP

MONEY_PLACES = Decimal(("0.01"))

# Convert to decimal
def to_decimal (text:str) -> Decimal: