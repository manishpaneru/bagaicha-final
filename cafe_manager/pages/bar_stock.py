"""
Bar Stock page implementation for the Cafe Management System.
Handles bar inventory management and tracking.
"""

import customtkinter as ctk
from utils.constants import *
from database import DatabaseManager
from datetime import datetime
from tkinter import messagebox
import sqlite3

class AddBarItemDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Window setup
        self.title("Add Bar Item")
        self.geometry("400x600")
        self.resizable(False, False)
        
        # Initialize variables
        self.unit_type_var = ctk.StringVar(value="ML")
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="Add New Bar Item",
            font=("Helvetica", 20, "bold")
        ).pack(pady=(0, 20))
        
        # Item Name
        ctk.CTkLabel(main_frame, text="Item Name:").pack(anchor="w")
        self.name_entry = ctk.CTkEntry(main_frame, width=300)
        self.name_entry.pack(pady=(0, 20))
        
        # Unit Type
        ctk.CTkLabel(main_frame, text="Unit Type:").pack(anchor="w")
        
        unit_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        unit_frame.pack(fill="x", pady=(0, 20))
        
        for unit in ["ML", "PIECE", "PACKET"]:
            ctk.CTkRadioButton(
                unit_frame,
                text=unit,
                variable=self.unit_type_var,
                value=unit,
                command=self.on_unit_change
            ).pack(side="left", padx=10)
        
        # Initial Quantity
        ctk.CTkLabel(main_frame, text="Initial Quantity:").pack(anchor="w")
        self.quantity_entry = ctk.CTkEntry(main_frame, width=300)
        self.quantity_entry.pack(pady=(0, 20))
        
        # Warning Threshold
        ctk.CTkLabel(main_frame, text="Warning Threshold:").pack(anchor="w")
        self.threshold_entry = ctk.CTkEntry(main_frame, width=300)
        self.threshold_entry.pack(pady=(0, 20))
        
        # Info text for packets
        self.packet_info = ctk.CTkLabel(
            main_frame,
            text="(1 packet = 20 pieces)",
            text_color="gray"
        )
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        # Save Button
        ctk.CTkButton(
            button_frame,
            text="Save Item",
            command=self.save_item,
            width=140,
            fg_color="#10B981"
        ).pack(side="left", padx=10, expand=True)
        
        # Cancel Button
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=140,
            fg_color="#EF4444"
        ).pack(side="right", padx=10, expand=True)
    
    def on_unit_change(self):
        """Handle unit type change"""
        if self.unit_type_var.get() == "PACKET":
            self.packet_info.pack(anchor="w")
        else:
            self.packet_info.pack_forget()
    
    def save_item(self):
        """Save new bar item"""
        try:
            name = self.name_entry.get().strip()
            unit_type = self.unit_type_var.get()
            
            try:
                quantity = float(self.quantity_entry.get())
                threshold = float(self.threshold_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
                return
            
            if not all([name, quantity > 0, threshold > 0]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            conn = self.parent.db.connect()
            cursor = conn.cursor()
            
            # Add item to bar_stock
            cursor.execute("""
                INSERT INTO bar_stock (
                    item_name, unit_type, pieces_per_packet,
                    quantity, original_quantity, min_threshold
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name, unit_type,
                20 if unit_type == "PACKET" else None,
                quantity, quantity, threshold
            ))
            
            conn.commit()
            messagebox.showinfo("Success", "Item added successfully!")
            
            self.parent.load_stock_data()
            self.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Item name already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def center_window(self):
        """Center the dialog window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class AddStockDialog(ctk.CTkToplevel):
    def __init__(self, parent, item_id):
        super().__init__(parent)
        self.parent = parent
        self.item_id = item_id
        
        # Window setup
        self.title("Add Stock")
        self.geometry("300x200")
        self.resizable(False, False)
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Get item details
        conn = self.parent.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_name, unit_type
            FROM bar_stock
            WHERE id = ?
        """, (self.item_id,))
        
        item_name, unit_type = cursor.fetchone()
        conn.close()
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text=f"Add Stock: {item_name}",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(0, 20))
        
        # Quantity
        ctk.CTkLabel(
            main_frame,
            text=f"Quantity ({unit_type}):"
        ).pack(anchor="w")
        
        self.quantity_entry = ctk.CTkEntry(main_frame, width=200)
        self.quantity_entry.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        
        # Add Button
        ctk.CTkButton(
            button_frame,
            text="Add Stock",
            command=self.add_stock,
            width=90,
            fg_color="#10B981"
        ).pack(side="left", padx=5, expand=True)
        
        # Cancel Button
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=90,
            fg_color="#EF4444"
        ).pack(side="right", padx=5, expand=True)
    
    def add_stock(self):
        """Add stock to existing item"""
        try:
            try:
                quantity = float(self.quantity_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
                return
            
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0")
                return
            
            conn = self.parent.db.connect()
            cursor = conn.cursor()
            
            # Update stock
            cursor.execute("""
                UPDATE bar_stock
                SET quantity = quantity + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (quantity, self.item_id))
            
            # Record in history
            cursor.execute("""
                INSERT INTO stock_history (
                    item_id, change_quantity,
                    operation_type, source
                ) VALUES (?, ?, 'add', 'expense')
            """, (self.item_id, quantity))
            
            conn.commit()
            messagebox.showinfo("Success", "Stock added successfully!")
            
            self.parent.load_stock_data()
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add stock: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def center_window(self):
        """Center the dialog window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class BarStockPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = DatabaseManager()
        
        # Initialize variables
        self.stock_items = []
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_stock_data()
    
    def setup_ui(self):
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header Frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20,0), sticky="ew")
        
        ctk.CTkLabel(
            header_frame,
            text="Bar Stock Management",
            font=("Helvetica", 24, "bold")
        ).pack(side="left")
        
        # Add Item Button
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Add Bar Item",
            command=self.show_add_item_dialog,
            width=150
        )
        add_btn.pack(side="right")
        
        # Stock Table
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        # Headers
        headers = ["Item Name", "Unit Type", "Original", "Remaining", 
                  "Warning Level", "Status", "Actions"]
        
        for col, text in enumerate(headers):
            ctk.CTkLabel(
                self.table_frame,
                text=text,
                font=("Helvetica", 12, "bold")
            ).grid(row=0, column=col, padx=10, pady=5, sticky="w")
        
        # Scrollable frame for stock items
        self.stock_frame = ctk.CTkScrollableFrame(self.table_frame)
        self.stock_frame.grid(row=1, column=0, columnspan=len(headers),
                            sticky="nsew", padx=5, pady=5)
    
    def load_stock_data(self):
        """Load stock data from database"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, item_name, unit_type, pieces_per_packet,
                       quantity, original_quantity, min_threshold
                FROM bar_stock
                ORDER BY item_name
            """)
            
            self.stock_items = cursor.fetchall()
            self.update_stock_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stock data: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def update_stock_list(self):
        """Update stock list display"""
        # Clear current list
        for widget in self.stock_frame.winfo_children():
            widget.destroy()
        
        # Add stock items
        for row, item in enumerate(self.stock_items):
            item_id, name, unit_type, pieces, qty, orig_qty, threshold = item
            
            # Format quantity based on unit type
            if unit_type == "PACKET":
                qty_text = f"{qty:.0f} packets ({qty * pieces:.0f} pieces)"
                orig_text = f"{orig_qty:.0f} packets"
            else:
                qty_text = f"{qty:.0f} {unit_type}"
                orig_text = f"{orig_qty:.0f} {unit_type}"
            
            # Status text and color
            status = "Low Stock!" if qty <= threshold else "OK"
            status_color = "#EF4444" if qty <= threshold else "#10B981"
            
            # Create row items
            cols = [name, unit_type, orig_text, qty_text, 
                   f"{threshold:.0f} {unit_type}", status]
            
            for col, text in enumerate(cols):
                label = ctk.CTkLabel(
                    self.stock_frame,
                    text=text,
                    text_color=status_color if col == 5 else None
                )
                label.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            
            # Action buttons
            actions_frame = ctk.CTkFrame(self.stock_frame, fg_color="transparent")
            actions_frame.grid(row=row, column=len(cols), padx=10, pady=5)
            
            # Add Stock button
            ctk.CTkButton(
                actions_frame,
                text="Add Stock",
                width=100,
                command=lambda i=item_id: self.show_add_stock_dialog(i)
            ).pack(side="left", padx=5)
    
    def show_add_item_dialog(self):
        """Show dialog to add new bar item"""
        AddBarItemDialog(self)
    
    def show_add_stock_dialog(self, item_id):
        """Show dialog to add stock to existing item"""
        AddStockDialog(self, item_id)
