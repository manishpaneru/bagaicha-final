"""
Bar Stock page implementation for the Cafe Management System.
Handles inventory management and stock tracking.
"""

import customtkinter as ctk
from utils.constants import *
from database import DatabaseManager
from datetime import datetime
from tkinter import messagebox
import sqlite3

class StockOperationDialog(ctk.CTkToplevel):
    """Dialog for adding or removing stock."""
    
    def __init__(self, parent, item_id, item_name, operation_type):
        super().__init__(parent)
        self.parent = parent
        self.item_id = item_id
        self.operation_type = operation_type  # 'add' or 'remove'
        
        # Window setup
        self.title(f"{'Add to' if operation_type == 'add' else 'Remove from'} {item_name}")
        self.geometry("300x200")
        self.resizable(False, False)
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Create and arrange UI components."""
        # Quantity entry
        ctk.CTkLabel(
            self,
            text=f"{'Add' if self.operation_type == 'add' else 'Remove'} Quantity:"
        ).pack(pady=(20,5))
        
        self.quantity_entry = ctk.CTkEntry(self)
        self.quantity_entry.pack(pady=5)
        
        # Confirm button
        ctk.CTkButton(
            self,
            text="Confirm",
            command=self.confirm_operation
        ).pack(pady=20)
    
    def confirm_operation(self):
        """Validate and confirm the stock operation."""
        try:
            quantity = float(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
            
            self.parent.update_stock(self.item_id, quantity, self.operation_type)
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

class AddStockDialog(ctk.CTkToplevel):
    """Dialog for adding new stock items."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Window setup
        self.title("Add Stock Item")
        self.geometry("400x400")
        self.resizable(False, False)
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Create and arrange UI components."""
        # Item name
        ctk.CTkLabel(self, text="Item Name:").pack(pady=(20,5))
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.pack(pady=5)
        
        # Initial quantity
        ctk.CTkLabel(self, text="Initial Quantity:").pack(pady=(10,5))
        self.quantity_entry = ctk.CTkEntry(self)
        self.quantity_entry.pack(pady=5)
        
        # Minimum threshold
        ctk.CTkLabel(self, text="Minimum Threshold:").pack(pady=(10,5))
        self.threshold_entry = ctk.CTkEntry(self)
        self.threshold_entry.pack(pady=5)
        
        # Save button
        ctk.CTkButton(
            self,
            text="Add Item",
            command=self.save_item
        ).pack(pady=20)
    
    def save_item(self):
        """Validate and save the new stock item."""
        try:
            name = self.name_entry.get().strip()
            quantity = float(self.quantity_entry.get())
            threshold = float(self.threshold_entry.get())
            
            if not name:
                raise ValueError("Please enter an item name")
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            if threshold < 0:
                raise ValueError("Threshold cannot be negative")
            
            self.parent.add_stock_item(name, quantity, threshold)
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

class BarStockPage(ctk.CTkFrame):
    """Bar Stock page showing inventory management."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = DatabaseManager()
        
        # Initialize variables
        self.stock_items = []
        self.low_stock_items = []
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_stock_data()
    
    def setup_ui(self):
        """Create and arrange all UI components."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Give table row the most weight
        
        # Create header
        self.create_header()
        
        # Create stock table
        self.create_stock_table()
        
        # Create low stock alerts section
        self.create_alerts_section()
    
    def create_header(self):
        """Create page header with Add Stock Item button."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(10,5), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Add Item Button
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Add Stock Item",
            command=self.show_add_item_dialog
        )
        add_btn.grid(row=0, column=1, padx=10, sticky="e")
    
    def create_stock_table(self):
        """Create scrollable stock table."""
        # Table container
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(1, weight=1)
        
        # Headers
        headers = ["Item Name", "Current Stock", "Min Threshold", "Status", "Last Updated", "Actions"]
        header_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Configure header columns
        for i in range(len(headers)):
            header_frame.grid_columnconfigure(i, weight=1 if i == 0 else 0)  # Give more space to Item Name
        
        # Create header labels
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=FONTS["body"]
            ).grid(row=0, column=i, padx=10, pady=5, sticky="w")
        
        # Scrollable frame for stock items
        self.stock_frame = ctk.CTkScrollableFrame(self.table_frame)
        self.stock_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure columns in stock frame
        for i in range(len(headers)):
            self.stock_frame.grid_columnconfigure(i, weight=1 if i == 0 else 0)
    
    def create_alerts_section(self):
        """Create low stock alerts section."""
        self.alerts_frame = ctk.CTkFrame(self)
        self.alerts_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        # Title
        ctk.CTkLabel(
            self.alerts_frame,
            text="Low Stock Alerts",
            font=FONTS["subheading"]
        ).pack(pady=10)
    
    def load_stock_data(self):
        """Load stock items from database."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, item_name, quantity, min_threshold, last_updated
                FROM bar_stock
                ORDER BY item_name
            """)
            
            self.stock_items = cursor.fetchall()
            self.update_stock_list()
            self.check_low_stock()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stock data: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def update_stock(self, item_id, quantity_change, operation_type):
        """Update stock quantity."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN")
            
            # Update stock quantity
            if operation_type == "add":
                cursor.execute("""
                    UPDATE bar_stock
                    SET quantity = quantity + ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (quantity_change, item_id))
            else:  # remove
                # Check if enough stock
                cursor.execute("SELECT quantity FROM bar_stock WHERE id = ?", (item_id,))
                current_quantity = cursor.fetchone()[0]
                if current_quantity < quantity_change:
                    raise ValueError("Not enough stock available")
                
                cursor.execute("""
                    UPDATE bar_stock
                    SET quantity = quantity - ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (quantity_change, item_id))
            
            # Record in stock history
            cursor.execute("""
                INSERT INTO stock_history (
                    item_id, change_quantity, operation_type
                ) VALUES (?, ?, ?)
            """, (item_id, quantity_change, operation_type))
            
            conn.commit()
            messagebox.showinfo("Success", "Stock updated successfully")
            self.load_stock_data()  # Refresh display
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("Error", f"Failed to update stock: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def add_stock_item(self, name, quantity, threshold):
        """Add new stock item to database."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO bar_stock (
                    item_name, quantity, min_threshold
                ) VALUES (?, ?, ?)
            """, (name, quantity, threshold))
            
            conn.commit()
            messagebox.showinfo("Success", "Stock item added successfully")
            self.load_stock_data()  # Refresh display
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "An item with this name already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add stock item: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def show_add_item_dialog(self):
        """Show dialog for adding new stock item."""
        dialog = AddStockDialog(self)
        dialog.focus()
    
    def show_stock_operation_dialog(self, item_id, item_name, operation_type):
        """Show dialog for adding/removing stock."""
        dialog = StockOperationDialog(self, item_id, item_name, operation_type)
        dialog.focus()
    
    def update_stock_list(self):
        """Update stock list display."""
        # Clear current list
        for widget in self.stock_frame.winfo_children():
            widget.destroy()
        
        # Add stock items to list
        for row, item in enumerate(self.stock_items):
            item_id, name, quantity, threshold, last_updated = item
            
            # Create frame for this row
            item_frame = ctk.CTkFrame(self.stock_frame, fg_color="transparent")
            item_frame.grid(row=row, column=0, columnspan=6, sticky="ew", pady=2)
            
            # Configure columns
            for i in range(6):
                item_frame.grid_columnconfigure(i, weight=1 if i == 0 else 0)
            
            # Item name
            ctk.CTkLabel(
                item_frame,
                text=name,
                font=FONTS["body"]
            ).grid(row=0, column=0, padx=10, sticky="w")
            
            # Current stock
            ctk.CTkLabel(
                item_frame,
                text=str(quantity),
                font=FONTS["body"]
            ).grid(row=0, column=1, padx=10, sticky="w")
            
            # Min threshold
            ctk.CTkLabel(
                item_frame,
                text=str(threshold),
                font=FONTS["body"]
            ).grid(row=0, column=2, padx=10, sticky="w")
            
            # Status
            status_color = COLORS["error"] if quantity <= threshold else COLORS["success"]
            status_text = "Low Stock" if quantity <= threshold else "In Stock"
            ctk.CTkLabel(
                item_frame,
                text=status_text,
                text_color=status_color,
                font=FONTS["body"]
            ).grid(row=0, column=3, padx=10, sticky="w")
            
            # Last updated
            ctk.CTkLabel(
                item_frame,
                text=last_updated,
                font=FONTS["body"]
            ).grid(row=0, column=4, padx=10, sticky="w")
            
            # Action buttons
            action_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            action_frame.grid(row=0, column=5, padx=10, sticky="e")
            
            # Add stock button
            ctk.CTkButton(
                action_frame,
                text="Add",
                width=60,
                command=lambda i=item_id, n=name: self.show_stock_operation_dialog(i, n, "add")
            ).pack(side="left", padx=2)
            
            # Remove stock button
            ctk.CTkButton(
                action_frame,
                text="Remove",
                width=60,
                fg_color=COLORS["error"],
                hover_color="#D32F2F",
                command=lambda i=item_id, n=name: self.show_stock_operation_dialog(i, n, "remove")
            ).pack(side="left", padx=2)
    
    def check_low_stock(self):
        """Check for items below minimum threshold."""
        self.low_stock_items = [
            item for item in self.stock_items
            if item[2] <= item[3]  # quantity <= min_threshold
        ]
        self.update_alerts()
    
    def update_alerts(self):
        """Update low stock alerts display."""
        # Clear current alerts
        for widget in self.alerts_frame.winfo_children()[1:]:  # Keep the title
            widget.destroy()
        
        if not self.low_stock_items:
            ctk.CTkLabel(
                self.alerts_frame,
                text="No low stock items",
                text_color=COLORS["text"]["secondary"]
            ).pack(pady=10)
        else:
            for item in self.low_stock_items:
                self.create_alert_item(item)
    
    def create_alert_item(self, item):
        """Create alert item display."""
        item_frame = ctk.CTkFrame(self.alerts_frame)
        item_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            item_frame,
            text=f"{item[1]}",  # Item name
            text_color=COLORS["error"]
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            item_frame,
            text=f"Current: {item[2]} | Min: {item[3]}",
            text_color=COLORS["text"]["secondary"]
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            item_frame,
            text="Add Stock",
            width=80,
            command=lambda: self.show_stock_operation_dialog(item[0], item[1], "add")
        ).pack(side="right", padx=5)
