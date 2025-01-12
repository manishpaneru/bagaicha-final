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
        self.db = DatabaseManager()
        
        # Window setup
        self.title("Add Expense")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Initialize variables
        self.category_var = ctk.StringVar(value="Management")  # Default value
        self.total_amount = 0.0
        
        self.setup_ui()
        self.center_window()

    def on_category_change(self, choice):
        """Handle category selection changes"""
        print(f"Selected category: {choice}")
        # You can add specific behavior for different categories here
        if choice == "Bar":
            # Maybe show additional fields or change validation rules
            pass
    
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="Add New Expense",
            font=("Helvetica", 20, "bold")
        ).pack(pady=(0, 20))
        
        # Name Field
        ctk.CTkLabel(main_frame, text="Name:").pack(anchor="w", pady=(10, 0))
        self.name_entry = ctk.CTkEntry(main_frame, width=300)
        self.name_entry.pack(pady=(0, 10))
        
        # Category Selection
        ctk.CTkLabel(main_frame, text="Category:").pack(anchor="w", pady=(10, 0))
        categories = ['Management', 'Miscellaneous', 'Bar', 'Kitchen']
        self.category_menu = ctk.CTkOptionMenu(
            main_frame,
            variable=self.category_var,
            values=categories,
            width=300,
            command=self.on_category_change  # Now this method exists
        )
        self.category_menu.pack(pady=(0, 10))
        
        # Quantity Field
        ctk.CTkLabel(main_frame, text="Quantity:").pack(anchor="w", pady=(10, 0))
        self.quantity_entry = ctk.CTkEntry(main_frame, width=300)
        self.quantity_entry.pack(pady=(0, 10))
        self.quantity_entry.bind('<KeyRelease>', self.calculate_total)
        
        # Price per Unit Field
        ctk.CTkLabel(main_frame, text="Price per Unit:").pack(anchor="w", pady=(10, 0))
        self.price_entry = ctk.CTkEntry(main_frame, width=300)
        self.price_entry.pack(pady=(0, 10))
        self.price_entry.bind('<KeyRelease>', self.calculate_total)
        
        # Total Amount Display
        ctk.CTkLabel(main_frame, text="Total Amount:").pack(anchor="w", pady=(10, 0))
        self.total_label = ctk.CTkLabel(
            main_frame,
            text="₹0.00",
            font=("Helvetica", 16, "bold")
        )
        self.total_label.pack(pady=(0, 20))
        
        # Buttons Frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20)
        
        # Save Button
        self.save_button = ctk.CTkButton(
            buttons_frame,
            text="Save Expense",
            command=self.save_expense,
            width=200,
            height=40,
            fg_color="#10B981",
            hover_color="#059669"
        )
        self.save_button.pack(side="left", padx=10, expand=True)
        
        # Cancel Button
        self.cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.destroy,
            width=200,
            height=40,
            fg_color="#EF4444",
            hover_color="#DC2626"
        )
        self.cancel_button.pack(side="right", padx=10, expand=True)

    def calculate_total(self, event=None):
        """Calculate total amount based on quantity and price"""
        try:
            quantity = float(self.quantity_entry.get() or 0)
            price = float(self.price_entry.get() or 0)
            self.total_amount = quantity * price
            self.total_label.configure(text=f"₹{self.total_amount:.2f}")
        except ValueError:
            self.total_label.configure(text="₹0.00")

    def save_expense(self):
        """Save expense to database."""
        try:
            # Get and validate inputs
            name = self.name_entry.get().strip()
            title = self.title_entry.get().strip()
            category = self.category_var.get()
            
            try:
                quantity = float(self.quantity_entry.get())
                price = float(self.price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
                return
            
            if not all([name, title, category, quantity > 0, price > 0]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            conn = self.parent.db.connect()
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN")
            
            try:
                # Save expense
                cursor.execute("""
                    INSERT INTO expenses (
                        name, title, category,
                        quantity, price_per_unit,
                        total_price, expense_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    name, title, category,
                    quantity, price,
                    quantity * price,
                    self.date_entry.get_date()
                ))
                
                # If it's a bar expense, update stock
                if category == "Bar":
                    # Get unit type from input or dialog
                    unit_type = self.unit_type_var.get()  # Add this to dialog
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO bar_stock (
                            item_name, unit_type, pieces_per_packet,
                            quantity, original_quantity, min_threshold
                        ) VALUES (
                            ?, ?, ?, 
                            COALESCE((SELECT quantity FROM bar_stock WHERE item_name = ?) + ?, ?),
                            ?, ?
                        )
                    """, (
                        name, unit_type,
                        20 if unit_type == "PACKET" else None,
                        name, quantity, quantity,
                        quantity, quantity * 0.2  # Default threshold 20% of original
                    ))
                    
                    # Get the bar_stock id
                    cursor.execute("SELECT id FROM bar_stock WHERE item_name = ?", (name,))
                    bar_id = cursor.fetchone()[0]
                    
                    # Record in history
                    cursor.execute("""
                        INSERT INTO stock_history (
                            item_id, change_quantity,
                            operation_type, source
                        ) VALUES (?, ?, 'add', 'expense')
                    """, (bar_id, quantity))
                
                conn.commit()
                messagebox.showinfo("Success", "Expense saved successfully")
                
                self.parent.load_expenses()
                self.destroy()
                
            except Exception as e:
                conn.rollback()
                raise e
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save expense: {str(e)}")
        finally:
            if conn:
                conn.close()

    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

class AddBarExpenseDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = DatabaseManager()
        
        # Window setup
        self.title("Add Bar Expense")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="Add Bar Expense",
            font=("Helvetica", 20, "bold")
        ).pack(pady=(0, 20))
        
        # Drink Name
        ctk.CTkLabel(main_frame, text="Drink Name:").pack(anchor="w", pady=(10,0))
        self.name_entry = ctk.CTkEntry(main_frame, width=300)
        self.name_entry.pack(pady=(0, 15))
        
        # Quantity (ML)
        ctk.CTkLabel(main_frame, text="Quantity (ML):").pack(anchor="w", pady=(10,0))
        self.quantity_entry = ctk.CTkEntry(main_frame, width=300)
        self.quantity_entry.pack(pady=(0, 15))
        
        # Total Cost
        ctk.CTkLabel(main_frame, text="Total Cost (₹):").pack(anchor="w", pady=(10,0))
        self.cost_entry = ctk.CTkEntry(main_frame, width=300)
        self.cost_entry.pack(pady=(0, 20))
        
        # Buttons Frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20)
        
        # Save Button
        ctk.CTkButton(
            buttons_frame,
            text="Save Bar Expense",
            command=self.save_expense,
            fg_color="#10B981",
            hover_color="#059669",
            width=140,
            height=40
        ).pack(side="left", padx=10, expand=True)
        
        # Cancel Button
        ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#EF4444",
            hover_color="#DC2626",
            width=140,
            height=40
        ).pack(side="right", padx=10, expand=True)
    
    def save_expense(self):
        try:
            # Get and validate inputs
            name = self.name_entry.get().strip()
            quantity = self.quantity_entry.get().strip()
            cost = self.cost_entry.get().strip()
            
            if not all([name, quantity, cost]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            try:
                quantity = float(quantity)
                cost = float(cost)
                if quantity <= 0 or cost <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
                return
            
            conn = self.db.connect()
            cursor = conn.cursor()
            
            try:
                cursor.execute("BEGIN")
                
                # Save to expenses table
                cursor.execute("""
                    INSERT INTO expenses (
                        name, title, category, quantity,
                        price_per_unit, total_price, expense_date
                    ) VALUES (?, ?, ?, ?, ?, ?, DATE('now', 'localtime'))
                """, (
                    name,
                    f"{name} ({quantity}ML)",
                    "Bar",
                    quantity,
                    cost/quantity,  # Price per ML
                    cost,
                ))
                
                # Update bar stock
                cursor.execute("""
                    INSERT OR REPLACE INTO bar_stock (
                        item_name, unit_type, quantity, original_quantity,
                        min_threshold, last_updated
                    ) VALUES (
                        ?, 'ML',
                        COALESCE((SELECT quantity FROM bar_stock WHERE item_name = ?) + ?, ?),
                        ?, ?, DATETIME('now', 'localtime')
                    )
                """, (
                    name, name, quantity, quantity,
                    quantity, quantity * 0.2  # 20% threshold
                ))
                
                # Get the bar_stock id
                cursor.execute("SELECT id FROM bar_stock WHERE item_name = ?", (name,))
                bar_id = cursor.fetchone()[0]
                
                # Record in history
                cursor.execute("""
                    INSERT INTO stock_history (
                        item_id, change_quantity, operation_type,
                        source, created_at
                    ) VALUES (?, ?, 'add', 'expense', DATETIME('now', 'localtime'))
                """, (bar_id, quantity))
                
                conn.commit()
                messagebox.showinfo("Success", "Bar expense added successfully!")
                
                if hasattr(self.parent, 'load_expenses'):
                    self.parent.load_expenses()
                
                self.destroy()
                
            except Exception as e:
                conn.rollback()
                raise e
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save expense: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

class AddCigaretteExpenseDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = DatabaseManager()
        
        # Window setup
        self.title("Add Cigarette Expense")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="Add Cigarette Expense",
            font=("Helvetica", 20, "bold")
        ).pack(pady=(0, 20))
        
        # Brand Name
        ctk.CTkLabel(main_frame, text="Brand Name:").pack(anchor="w", pady=(10,0))
        self.name_entry = ctk.CTkEntry(main_frame, width=300)
        self.name_entry.pack(pady=(0, 15))
        
        # Quantity (Packets)
        ctk.CTkLabel(main_frame, text="Quantity (Packets):").pack(anchor="w", pady=(10,0))
        self.quantity_entry = ctk.CTkEntry(main_frame, width=300)
        self.quantity_entry.pack(pady=(0, 15))
        
        # Total Cost
        ctk.CTkLabel(main_frame, text="Total Cost (₹):").pack(anchor="w", pady=(10,0))
        self.cost_entry = ctk.CTkEntry(main_frame, width=300)
        self.cost_entry.pack(pady=(0, 20))
        
        # Info Label
        ctk.CTkLabel(
            main_frame,
            text="(1 packet = 20 pieces)",
            text_color="gray"
        ).pack(pady=(0, 20))
        
        # Buttons Frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20)
        
        # Save Button
        ctk.CTkButton(
            buttons_frame,
            text="Save Cigarette Expense",
            command=self.save_expense,
            fg_color="#10B981",
            hover_color="#059669",
            width=140,
            height=40
        ).pack(side="left", padx=10, expand=True)
        
        # Cancel Button
        ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#EF4444",
            hover_color="#DC2626",
            width=140,
            height=40
        ).pack(side="right", padx=10, expand=True)
    
    def save_expense(self):
        try:
            # Get and validate inputs
            name = self.name_entry.get().strip()
            packets = self.quantity_entry.get().strip()
            cost = self.cost_entry.get().strip()
            
            if not all([name, packets, cost]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            try:
                packets = int(packets)
                cost = float(cost)
                if packets <= 0 or cost <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
                return
            
            conn = self.db.connect()
            cursor = conn.cursor()
            
            try:
                cursor.execute("BEGIN")
                
                pieces = packets * 20  # Convert packets to pieces
                
                # Save to expenses table
                cursor.execute("""
                    INSERT INTO expenses (
                        name, title, category, quantity,
                        price_per_unit, total_price, expense_date
                    ) VALUES (?, ?, ?, ?, ?, ?, DATE('now', 'localtime'))
                """, (
                    name,
                    f"{name} ({packets} packets)",
                    "Cigarette",
                    pieces,  # Store as pieces
                    cost/pieces,  # Cost per piece
                    cost,
                ))
                
                # Update bar stock
                cursor.execute("""
                    INSERT OR REPLACE INTO bar_stock (
                        item_name, unit_type, pieces_per_packet,
                        quantity, original_quantity, min_threshold,
                        last_updated
                    ) VALUES (
                        ?, 'PACKET', 20,
                        COALESCE((SELECT quantity FROM bar_stock WHERE item_name = ?) + ?, ?),
                        ?, ?, DATETIME('now', 'localtime')
                    )
                """, (
                    name, name, pieces, pieces,
                    pieces, pieces * 0.2  # 20% threshold
                ))
                
                # Get the bar_stock id
                cursor.execute("SELECT id FROM bar_stock WHERE item_name = ?", (name,))
                bar_id = cursor.fetchone()[0]
                
                # Record in history
                cursor.execute("""
                    INSERT INTO stock_history (
                        item_id, change_quantity, operation_type,
                        source, created_at
                    ) VALUES (?, ?, 'add', 'expense', DATETIME('now', 'localtime'))
                """, (bar_id, pieces))
                
                conn.commit()
                messagebox.showinfo("Success", "Cigarette expense added successfully!")
                
                if hasattr(self.parent, 'load_expenses'):
                    self.parent.load_expenses()
                
                self.destroy()
                
            except Exception as e:
                conn.rollback()
                raise e
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save expense: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

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
        self.grid_rowconfigure(1, weight=1)  # Give table row the most weight
        
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
        
        # Title
        ctk.CTkLabel(
            header_frame,
            text="Expense Management",
            font=("Helvetica", 24, "bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Buttons Frame
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="e")
        
        # Add General Expense Button
        ctk.CTkButton(
            buttons_frame,
            text="+ Add Expense",
            command=self.show_add_expense_dialog,
            width=120
        ).pack(side="right", padx=5)
        
        # Add Bar Expense Button
        ctk.CTkButton(
            buttons_frame,
            text="+ Bar Expense",
            command=self.show_bar_expense_dialog,
            width=120
        ).pack(side="right", padx=5)
        
        # Add Cigarette Expense Button
        ctk.CTkButton(
            buttons_frame,
            text="+ Cigarette Expense",
            command=self.show_cigarette_expense_dialog,
            width=120
        ).pack(side="right", padx=5)
    
    def create_expense_table(self):
        """Create scrollable expense table."""
        # Table container
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(1, weight=1)
        
        # Table headers
        headers = ["Name", "Category", "Title", "Quantity", "Price/Unit", "Total", "Date", "Actions"]
        header_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Configure header columns
        for i in range(len(headers)):
            header_frame.grid_columnconfigure(i, weight=1 if i < 3 else 0)  # Give more space to Name, Category, and Title
        
        # Create header labels
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=FONTS["body"]
            ).grid(row=0, column=i, padx=10, pady=5, sticky="w")
        
        # Scrollable frame for expenses
        self.expense_frame = ctk.CTkScrollableFrame(self.table_frame)
        self.expense_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure columns in expense frame
        for i in range(len(headers)):
            self.expense_frame.grid_columnconfigure(i, weight=1 if i < 3 else 0)
    
    def create_total_section(self):
        """Create total expenses display."""
        total_frame = ctk.CTkFrame(self)
        total_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.total_label = ctk.CTkLabel(
            total_frame,
            text="Total Expenses Today: ₹0.00",
            font=FONTS["subheading"]
        )
        self.total_label.pack(pady=5)
    
    def load_expenses(self):
        """Load expenses from database."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, category, title, quantity, price_per_unit, 
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
    
    def add_expense(self, name, category, title, quantity, price_per_unit):
        """Add new expense to database."""
        try:
            total_price = quantity * price_per_unit
            
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN")
            
            # Add to expenses table
            cursor.execute("""
                INSERT INTO expenses (
                    name, category, title, quantity, price_per_unit, 
                    total_price, expense_date
                ) VALUES (?, ?, ?, ?, ?, ?, DATE('now', 'localtime'))
            """, (name, category, title, quantity, price_per_unit, total_price))
            
            # If Bar category, update bar_stock
            if category == 'Bar':
                # Check if item exists in bar_stock
                cursor.execute("""
                    SELECT id, quantity FROM bar_stock
                    WHERE item_name = ?
                """, (name,))
                
                stock_item = cursor.fetchone()
                
                if stock_item:
                    # Update existing item
                    cursor.execute("""
                        UPDATE bar_stock
                        SET quantity = quantity + ?,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (quantity, stock_item[0]))
                else:
                    # Add new item
                    cursor.execute("""
                        INSERT INTO bar_stock (
                            item_name, quantity, min_threshold
                        ) VALUES (?, ?, 10)
                    """, (name, quantity))
                
                # Add to stock history
                cursor.execute("""
                    INSERT INTO stock_history (
                        item_id, change_quantity, operation_type
                    ) VALUES (
                        (SELECT id FROM bar_stock WHERE item_name = ?),
                        ?, 'add'
                    )
                """, (name, quantity))
            
            conn.commit()
            self.load_expenses()  # Refresh list
            
        except Exception as e:
            if conn:
                conn.rollback()
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
        dialog.grab_set()
        dialog.focus_force()
    
    def update_expense_list(self):
        """Update expense list display."""
        # Clear current list
        for widget in self.expense_frame.winfo_children():
            widget.destroy()
        
        # Add expenses to list
        for row, expense in enumerate(self.expenses):
            expense_frame = ctk.CTkFrame(self.expense_frame, fg_color="transparent")
            expense_frame.grid(row=row, column=0, columnspan=8, sticky="ew", pady=2)
            
            # Configure columns
            for i in range(8):
                expense_frame.grid_columnconfigure(i, weight=1 if i < 3 else 0)
            
            # Add expense data
            values = [
                expense[1],  # Name
                expense[2],  # Category
                expense[3],  # Title
                str(expense[4]),  # Quantity
                f"₹{expense[5]:,.2f}",  # Price/Unit
                f"₹{expense[6]:,.2f}",  # Total
                expense[7]  # Date
            ]
            
            for col, value in enumerate(values):
                ctk.CTkLabel(
                    expense_frame,
                    text=value,
                    font=FONTS["body"]
                ).grid(row=0, column=col, padx=10, sticky="w")
            
            # Add delete button
            ctk.CTkButton(
                expense_frame,
                text="Delete",
                fg_color=COLORS["error"],
                hover_color="#D32F2F",
                width=80,
                command=lambda id=expense[0]: self.delete_expense(id)
            ).grid(row=0, column=7, padx=10)
    
    def calculate_total(self):
        """Calculate and update total expenses."""
        self.total_expenses = sum(expense[6] for expense in self.expenses)
        self.total_label.configure(
            text=f"Total Expenses Today: ₹{self.total_expenses:,.2f}"
        )
    
    def show_bar_expense_dialog(self):
        dialog = AddBarExpenseDialog(self)
        dialog.grab_set()
    
    def show_cigarette_expense_dialog(self):
        dialog = AddCigaretteExpenseDialog(self)
        dialog.grab_set()
