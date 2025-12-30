from dataclasses import dataclass
from datetime import  datetime
from typing import Optional

@dataclass
class transaction:
    """M-Pesa transaction data model"""
    transaction_code:str
    amount:float
    date:datetime
    fee:float
    transaction_type:str # Sent, Received, Withdrawn, etc.

    def to_dict(self):
        return{
           'transaction_code':self.transaction_code,
           'amount:float':self.amount,
           'date:datetime':self.date.strftime('%Y-%m-%d %H:%M:%S'),
           'fee:float':self.fee,
           'transaction_type:str':self.transaction_type
        }