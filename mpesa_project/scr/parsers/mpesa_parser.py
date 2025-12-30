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

@staticmethod
def clean_amount(amount_str: str) -> float:
    """Clean and convert amount string to float"""
    return float(amount_str.replace(',',''))

@staticmethod

def parse_date(date_str: str, time_str: str) -> datetime:
    """Parse date and time from Mpesa format"""

    try:
        date_formats = [
            '%d/%m/%y %I:%M %p',
            '%d/%m/%Y %I:%M %p',
            '%d/%m/%y %H:%M',
            '%d/%m/%Y %H:%M',
            ]
        datetime_str = f"{date_str} {time_str}".strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(datetime_str,fmt)
            except ValueError:
                continue

        return datetime.strptime(datetime_str,'%d/%m/%y %H:%M')
    
    except Exception as e:
        raise ValueError(f"Could not parse date: {date_str} {time_str}.Error:{e}")
    
def extract_field(self,message: str, pattern:str, group:int = 1) -> Optional[str]:
    """ Extract a field using the regex pattern """

    match = re.search(pattern, message, re.IGNORECASE)
    if match:
        return match.group(group).strip()
    return None
