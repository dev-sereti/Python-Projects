import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime
from scr.parsers.mpesa_parser import MPesaParser
from scr.database.db_manager import DatabaseManager
from scr.excel.excel_handler import ExcelHandler


class MPesaApp:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("M-Pesa Transaction Manager")
        self.root.geometry("900x700")
        
        # Initialize components
        self.parser = MPesaParser()
        self.db_manager = DatabaseManager()
        self.excel_handler = None
        
        self.setup_ui()
        self.load_statistics()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=("nsww"))
        
        # Title
        title = ttk.Label(main_frame, text="M-Pesa Transaction Manager", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Excel file selection
        excel_frame = ttk.LabelFrame(main_frame, text="Excel File", padding="5")
        excel_frame.grid(row=1, column=0, columnspan=2, sticky=("we"), pady=5)
        
        self.excel_path_var = tk.StringVar(value="transactions.xlsx")
        ttk.Entry(excel_frame, textvariable=self.excel_path_var, width=60).grid(
            row=0, column=0, padx=5)
        ttk.Button(excel_frame, text="Browse", command=self.browse_excel).grid(
            row=0, column=1, padx=5)
        ttk.Button(excel_frame, text="Export All", command=self.export_all).grid(
            row=0, column=2, padx=5)
        
        # Message input
        input_frame = ttk.LabelFrame(main_frame, text="Paste M-Pesa Messages", padding="5")
        input_frame.grid(row=2, column=0, columnspan=2, sticky=("nsew"), pady=5)
        
        self.message_text = scrolledtext.ScrolledText(input_frame, height=15, width=80)
        self.message_text.grid(row=0, column=0, sticky=("nsew"))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Parse & Save", command=self.parse_and_save,
                  style='Accent.TButton').grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_input).grid(
            row=0, column=1, padx=5)
        ttk.Button(button_frame, text="View All", command=self.view_all_transactions).grid(
            row=0, column=2, padx=5)
        
        # Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="5")
        stats_frame.grid(row=4, column=0, columnspan=2, sticky=("we"), pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=8, width=80)
        self.stats_text.grid(row=0, column=0)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=("we"), pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def browse_excel(self):
        """Browse for Excel file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.excel_path_var.set(filename)
    
    def get_excel_handler(self):
        """Get or create Excel handler"""
        if not self.excel_handler or self.excel_handler.excel_path != self.excel_path_var.get():
            self.excel_handler = ExcelHandler(self.excel_path_var.get())
        return self.excel_handler
    
    def parse_and_save(self):
        """Parse messages and save to database and Excel"""
        messages_text = self.message_text.get("1.0", tk.END).strip()
        
        if not messages_text:
            messagebox.showwarning("Warning", "Please paste M-Pesa messages first")
            return
        
        # Split messages (assuming each message is separated by newline or double newline)
        messages = [msg.strip() for msg in messages_text.split('\n\n') if msg.strip()]
        if not messages:
            messages = [messages_text]
        
        self.status_var.set("Parsing messages...")
        self.root.update()
        
        # Parse messages
        transactions = self.parser.parse_multiple_messages(messages)
        
        if not transactions:
            messagebox.showerror("Error", "Could not parse any valid transactions")
            self.status_var.set("Error: No valid transactions found")
            return
        
        # Save to database
        success, duplicates = self.db_manager.insert_multiple_transactions(transactions)
        
        # Save to Excel
        excel_handler = self.get_excel_handler()
        excel_success = excel_handler.append_transactions(transactions)
        
        # Show results
        message = f"Successfully processed:\n"
        message += f"- New transactions: {success}\n"
        message += f"- Duplicates skipped: {duplicates}\n"
        message += f"- Excel updated: {'Yes' if excel_success else 'No'}"
        
        messagebox.showinfo("Success", message)
        self.status_var.set(f"Saved {success} new transactions")
        
        # Clear input and reload statistics
        self.clear_input()
        self.load_statistics()
    
    def clear_input(self):
        """Clear the message input"""
        self.message_text.delete("1.0", tk.END)
    
    def load_statistics(self):
        """Load and display statistics"""
        stats = self.db_manager.get_statistics()
        
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, f"Total Transactions: {stats['total_transactions']}\n")
        self.stats_text.insert(tk.END, f"Total Amount: KSh {stats['total_amount']:,.2f}\n")
        self.stats_text.insert(tk.END, f"Total Fees: KSh {stats['total_fees']:,.2f}\n\n")
        self.stats_text.insert(tk.END, "By Transaction Type:\n")
        
        for item in stats['by_type']:
            self.stats_text.insert(tk.END, 
                f"  {item['transaction_type'].capitalize()}: "
                f"{item['count']} transactions, KSh {item['total']:,.2f}\n")
    
    def view_all_transactions(self):
        """Open window to view all transactions"""
        ViewTransactionsWindow(self.root, self.db_manager)
    
    def export_all(self):
        """Export all database records to Excel"""
        excel_handler = self.get_excel_handler()
        if excel_handler.export_from_database(self.db_manager):
            messagebox.showinfo("Success", "All transactions exported to Excel")
            self.status_var.set("Exported to Excel successfully")
        else:
            messagebox.showerror("Error", "Failed to export to Excel")


class ViewTransactionsWindow:
    """Window to view all transactions"""
    
    def __init__(self, parent, db_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("All Transactions")
        self.window.geometry("1000x600")
        
        self.db_manager = db_manager
        
        # Create treeview
        columns = ('Code', 'Date', 'Type', 'Amount', 'Fee', 'Sender', 'Recipient', 'Balance')
        
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings', height=25)
        
        # Define headings
        self.tree.heading('Code', text='Transaction Code')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Amount', text='Amount')
        self.tree.heading('Fee', text='Fee')
        self.tree.heading('Sender', text='Sender')
        self.tree.heading('Recipient', text='Recipient')
        self.tree.heading('Balance', text='Balance')
        
        # Define column widths
        self.tree.column('Code', width=120)
        self.tree.column('Date', width=150)
        self.tree.column('Type', width=100)
        self.tree.column('Amount', width=100)
        self.tree.column('Fee', width=80)
        self.tree.column('Sender', width=150)
        self.tree.column('Recipient', width=150)
        self.tree.column('Balance', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky=("nsew"))
        scrollbar.grid(row=0, column=1, sticky=("ns"))
        
        # Configure grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load transactions into treeview"""
        transactions = self.db_manager.get_all_transactions()
        
        for trans in transactions:
            self.tree.insert('', tk.END, values=(
                trans['transaction_code'],
                trans['date'],
                trans['transaction_type'].capitalize(),
                f"KSh {trans['amount']:,.2f}",
                f"KSh {trans['fee']:,.2f}",
                trans['sender'] or '',
                trans['recipient'] or '',
                f"KSh {trans['balance']:,.2f}" if trans['balance'] else ''
            ))