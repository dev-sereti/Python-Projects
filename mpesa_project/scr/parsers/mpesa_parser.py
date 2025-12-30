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

        }
    }

