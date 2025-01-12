"""
Expenses page implementation for the Cafe Management System.
Handles expense tracking and management.
"""

import customtkinter as ctk
from utils.constants import *
from database import DatabaseManager
from datetime import datetime
from tkinter import messagebox
import sqlite3

class AddExpenseDialog(ctk.CTkToplevel):
    """Dialog for adding new expenses."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Window setup
        self.title("Add Expense")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Create and arrange all UI components."""
        # Name entry
        ctk.CTkLabel(self, text="Name:").pack(pady=(20,5))
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.pack(pady=5)
        
        # Title entry
        ctk.CTkLabel(self, text="Title:").pack(pady=(10,5))
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.pack(pady=5)
        
        # Quantity entry
        ctk.CTkLabel(self, text="Quantity:").pack(pady=(10,5))
        self.quantity_entry = ctk.CTkEntry(self)
        self.quantity_entry.pack(pady=5)
        
        # Price per unit entry
        ctk.CTkLabel(self, text="Price per Unit:").pack(pady=(10,5))
        self.price_entry = ctk.CTkEntry(self)
        self.price_entry.pack(pady=5)
        
        # Save button
        ctk.CTkButton(
            self,
            text="Save Expense",
            command=self.save_expense
        ).pack(pady=20)
    
    def save_expense(self):
        """Validate and save the expense."""
        try:
            name = self.name_entry.get().strip()
            title = self.title_entry.get().strip()
            quantity = float(self.quantity_entry.get())
            price = float(self.price_entry.get())
            
            if not all([name, title, quantity > 0, price > 0]):
                raise ValueError("Please fill all fields with valid values")
            
            self.parent.add_expense(name, title, quantity, price)
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

class ExpensesPage(ctk.CTkFrame):
    """Expenses page showing expense tracking and management."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = DatabaseManager()
        
        # Initialize variables
        self.expenses = []
        self.total_expenses = 0.0
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_expenses()
    
    def setup_ui(self):
        """Create and arrange all UI components."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create header frame
        self.create_header()
        
        # Create expense table
        self.create_expense_table()
        
        # Create total section
        self.create_total_section()
    
    def create_header(self):
        """Create page header with Add Expense button."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20,0), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Add Expense Button
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Add Expense",
            command=self.show_add_expense_dialog
        )
        add_btn.grid(row=0, column=1, padx=10, sticky="e")
    
    def create_expense_table(self):
        """Create scrollable expense table."""
        # Table container
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        # Table headers
        headers = ["Name", "Title", "Quantity", "Price/Unit", "Total", "Date", "Actions"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=FONTS["body"]
            ).grid(row=0, column=i, padx=10, pady=5, sticky="w")
        
        # Scrollable frame for expenses
        self.expense_frame = ctk.CTkScrollableFrame(self.table_frame)
        self.expense_frame.grid(row=1, column=0, columnspan=len(headers), 
                              sticky="nsew", padx=5, pady=5)
    
    def create_total_section(self):
        """Create total expenses display."""
        total_frame = ctk.CTkFrame(self)
        total_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        self.total_label = ctk.CTkLabel(
            total_frame,
            text="Total Expenses Today: ₹0.00",
            font=FONTS["subheading"]
        )
        self.total_label.pack(pady=10)
    
    def load_expenses(self):
        """Load expenses from database."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, title, quantity, price_per_unit, 
                       total_price, expense_date
                FROM expenses
                WHERE DATE(expense_date) = DATE('now', 'localtime')
                ORDER BY expense_date DESC
            """)
            
            self.expenses = cursor.fetchall()
            self.update_expense_list()
            self.calculate_total()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expenses: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def add_expense(self, name, title, quantity, price_per_unit):
        """Add new expense to database."""
        try:
            total_price = quantity * price_per_unit
            
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO expenses (
                    name, title, quantity, price_per_unit, 
                    total_price, expense_date
                ) VALUES (?, ?, ?, ?, ?, DATE('now', 'localtime'))
            """, (name, title, quantity, price_per_unit, total_price))
            
            conn.commit()
            messagebox.showinfo("Success", "Expense added successfully")
            self.load_expenses()  # Refresh list
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add expense: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def delete_expense(self, expense_id):
        """Delete expense from database."""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            try:
                conn = self.db.connect()
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                conn.commit()
                
                messagebox.showinfo("Success", "Expense deleted successfully")
                self.load_expenses()  # Refresh list
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete expense: {str(e)}")
            finally:
                if conn:
                    conn.close()
    
    def show_add_expense_dialog(self):
        """Show dialog for adding new expense."""
        dialog = AddExpenseDialog(self)
        dialog.focus()
    
    def update_expense_list(self):
        """Update expense list display."""
        # Clear current list
        for widget in self.expense_frame.winfo_children():
            widget.destroy()
        
        # Add expenses to list
        for row, expense in enumerate(self.expenses):
            for col, value in enumerate(expense[1:]):  # Skip ID
                if col == 4:  # Total price
                    text = f"₹{value:,.2f}"
                elif col == 3:  # Price per unit
                    text = f"₹{value:,.2f}"
                else:
                    text = str(value)
                
                ctk.CTkLabel(
                    self.expense_frame,
                    text=text
                ).grid(row=row, column=col, padx=10, pady=5, sticky="w")
            
            # Add delete button
            ctk.CTkButton(
                self.expense_frame,
                text="Delete",
                fg_color=COLORS["error"],
                hover_color="#D32F2F",
                width=80,
                command=lambda id=expense[0]: self.delete_expense(id)
            ).grid(row=row, column=6, padx=10, pady=5)
    
    def calculate_total(self):
        """Calculate and update total expenses."""
        self.total_expenses = sum(expense[5] for expense in self.expenses)
        self.total_label.configure(
            text=f"Total Expenses Today: ₹{self.total_expenses:,.2f}"
        )
