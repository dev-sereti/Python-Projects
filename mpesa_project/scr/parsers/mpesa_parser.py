import re
from datetime import datetime
from typing import Optional
from scr.models.transaction import Transaction

class MpesaParser:
    """Parse various M-Pesa message formats"""

    # Regex patterns for different transaction types
    PATTERNS = {
        'sent': {
            'code': r'([A-Z0-9]{10})\s+confirmed',
            'amount': r'Ksh([\d,]+\.?\d*)',
            'date': r'on\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+at\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)',
            'fee': r'Transaction cost[,:]?\s*Ksh([\d,]+\.?\d*)',
         },
        'received': {
            'code': r'([A-Z0-9]{10})\s+confirmed',
            'amount': r'Ksh([\d,]+\.?\d*)',
            'date': r'on\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+at\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)',
            'sender': r'from\s+(.+?)\s+on',
            'fee': r'0\.00',  # Usually no fee for received
        },
        'withdrawn': {
            'code': r'([A-Z0-9]{10})\s+confirmed',
            'amount': r'Ksh([\d,]+\.?\d*)',
            'date': r'on\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+at\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)',
            'fee': r'Transaction cost[,:]?\s*Ksh([\d,]+\.?\d*)',
            'agent': r'from\s+(.+?)\s+',
        },
         'paybill': {
            'code': r'([A-Z0-9]{10})\s+confirmed',
            'amount': r'Ksh([\d,]+\.?\d*)',
            'date': r'on\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+at\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)',
            'fee': r'Transaction cost[,:]?\s*Ksh([\d,]+\.?\d*)',
            'recipient': r'paid to\s+(.+?)(?:\.|on)',
            'account': r'Account\s+(.+?)\s*(?:on|\.|Transaction)',
        }
    }

@staticmethod
def detect_transaction_type(message: str)-> Optional[str]:
    """Detect the type of M-Pesa transaction"""
    message_lower = message.lower()

    if 'sent to' in message_lower:
        return 'sent'
    elif 'received' in message_lower and 'from' in message_lower:
        return 'received'
    elif 'withdaw' in message_lower:
        return 'withdrawn'
    elif 'paid to' in message_lower or 'paybill' in message_lower:
        return 'paybill'
    elif 'bought' in message_lower:
        return 'airtime'
    return None


 
