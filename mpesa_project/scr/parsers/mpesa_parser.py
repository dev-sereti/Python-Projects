import re
from datetime import datetime
from typing import Optional, List
from models.transaction import Transaction

class MPesaParser:
    """Parse various M-Pesa message formats"""
    
    # Regex patterns for different transaction types
    PATTERNS = {
        'sent': {
            'code': r'([A-Z0-9]{10})\s+confirmed',
            'amount': r'Ksh([\d,]+\.?\d*)',
            'date': r'on\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+at\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)',
            'fee': r'Transaction cost[,:]?\s*Ksh([\d,]+\.?\d*)',
            'recipient': r'sent to\s+(.+?)\s+on',
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
    def detect_transaction_type(message: str) -> Optional[str]:
        """Detect the type of M-Pesa transaction"""
        message_lower = message.lower()
        
        if 'sent to' in message_lower:
            return 'sent'
        elif 'received' in message_lower and 'from' in message_lower:
            return 'received'
        elif 'withdraw' in message_lower:
            return 'withdrawn'
        elif 'paid to' in message_lower or 'paybill' in message_lower:
            return 'paybill'
        elif 'bought' in message_lower:
            return 'airtime'
        
        return None
    
    @staticmethod
    def clean_amount(amount_str: str) -> float:
        """Clean and convert amount string to float"""
        return float(amount_str.replace(',', ''))
    
    @staticmethod
    def parse_date(date_str: str, time_str: str) -> datetime:
        """Parse date and time from M-Pesa format"""
        try:
            # Handle different date formats
            date_formats = [
                '%d/%m/%y %I:%M %p',
                '%d/%m/%Y %I:%M %p',
                '%d/%m/%y %H:%M',
                '%d/%m/%Y %H:%M',
            ]
            
            datetime_str = f"{date_str} {time_str}".strip()
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(datetime_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, try without AM/PM
            return datetime.strptime(datetime_str, '%d/%m/%y %H:%M')
            
        except Exception as e:
            raise ValueError(f"Could not parse date: {date_str} {time_str}. Error: {e}")
    
    def extract_field(self, message: str, pattern: str, group: int = 1) -> Optional[str]:
        """Extract a field using regex pattern"""
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(group).strip()
        return None
    
    def parse_message(self, message: str) -> Optional[Transaction]:
        """Parse M-Pesa message and return Transaction object"""
        try:
            # Detect transaction type
            trans_type = self.detect_transaction_type(message)
            
            if not trans_type or trans_type not in self.PATTERNS:
                raise ValueError(f"Unknown transaction type: {trans_type}")
            
            patterns = self.PATTERNS[trans_type]
            
            # Extract transaction code
            code = self.extract_field(message, patterns['code'])
            if not code:
                raise ValueError("Could not extract transaction code")
            
            # Extract amount
            amount_str = self.extract_field(message, patterns['amount'])
            if not amount_str:
                raise ValueError("Could not extract amount")
            amount = self.clean_amount(amount_str)
            
            # Extract date and time
            date_match = re.search(patterns['date'], message, re.IGNORECASE)
            if not date_match:
                raise ValueError("Could not extract date")
            
            date_str = date_match.group(1)
            time_str = date_match.group(2)
            transaction_date = self.parse_date(date_str, time_str)
            
            # Extract fee
            fee_str = self.extract_field(message, patterns['fee'])
            fee = self.clean_amount(fee_str) if fee_str else 0.0
            
            # Extract additional fields
            recipient = self.extract_field(message, patterns.get('recipient', ''))
            sender = self.extract_field(message, patterns.get('sender', ''))
            
            # Extract balance
            balance_match = re.search(r'balance.*?Ksh([\d,]+\.?\d*)', message, re.IGNORECASE)
            balance = self.clean_amount(balance_match.group(1)) if balance_match else None
            
            return Transaction(
                transaction_code=code,
                amount=amount,
                date=transaction_date,
                fee=fee,
                transaction_type=trans_type,
                recipient=recipient,
                sender=sender,
                balance=balance,
                message=message
            )
            
        except Exception as e:
            print(f"Error parsing message: {e}")
            return None
    
    def parse_multiple_messages(self, messages: List[str]) -> List[Transaction]:
        """Parse multiple messages"""
        transactions = []
        for msg in messages:
            transaction = self.parse_message(msg.strip())
            if transaction:
                transactions.append(transaction)
        return transactions