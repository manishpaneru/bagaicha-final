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
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Give table row the most weight
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_stock_data()
    
    def setup_ui(self):
        """Create and arrange all UI components."""
        # Header frame with title and add button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20,10), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        ctk.CTkLabel(
            header_frame,
            text="Bar Stock Management",
            font=("Helvetica", 24, "bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Add Bar Item Button
        ctk.CTkButton(
            header_frame,
            text="+ Add Bar Item",
            command=self.show_add_dialog,
            width=120
        ).grid(row=0, column=1, sticky="e")
        
        # Table container frame
        self.table_container = ctk.CTkFrame(self)
        self.table_container.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)
        
        # Headers frame
        headers_frame = ctk.CTkFrame(self.table_container, fg_color="transparent")
        headers_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Configure header columns
        headers = ["Item Name", "Unit Type", "Original", "Remaining", "Warning Level", "Status", "Actions"]
        for i in range(len(headers)):
            headers_frame.grid_columnconfigure(i, weight=1)
        
        # Create headers
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=("Helvetica", 12, "bold")
            ).grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Create scrollable frame for stock items
        self.stock_frame = ctk.CTkScrollableFrame(self.table_container)
        self.stock_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        
        # Configure columns in stock frame
        for i in range(len(headers)):
            self.stock_frame.grid_columnconfigure(i, weight=1)
    
    def load_stock_data(self):
        """Load and display stock data"""
        try:
            # Clear existing items
            for widget in self.stock_frame.winfo_children():
                widget.destroy()
            
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, item_name, unit_type, pieces_per_packet,
                    original_quantity, quantity, min_threshold
                FROM bar_stock
                ORDER BY item_name
            """)
            
            for i, row in enumerate(cursor.fetchall()):
                item_id, name, unit_type, pieces, original, remaining, threshold = row
                
                # Item name
                ctk.CTkLabel(
                    self.stock_frame,
                    text=name
                ).grid(row=i, column=0, padx=5, pady=5, sticky="w")
                
                # Unit type
                ctk.CTkLabel(
                    self.stock_frame,
                    text=unit_type
                ).grid(row=i, column=1, padx=5, pady=5, sticky="w")
                
                # Original quantity
                if unit_type == "PACKET":
                    original_text = f"{original} packets ({original * 20} pieces)"
                    remaining_text = f"{remaining} packets ({remaining * 20} pieces)"
                    threshold_text = f"{threshold} packets ({threshold * 20} pieces)"
                else:
                    original_text = f"{original} {unit_type}"
                    remaining_text = f"{remaining} {unit_type}"
                    threshold_text = f"{threshold} {unit_type}"
                
                ctk.CTkLabel(
                    self.stock_frame,
                    text=original_text
                ).grid(row=i, column=2, padx=5, pady=5, sticky="w")
                
                # Remaining quantity
                ctk.CTkLabel(
                    self.stock_frame,
                    text=remaining_text
                ).grid(row=i, column=3, padx=5, pady=5, sticky="w")
                
                # Warning threshold
                ctk.CTkLabel(
                    self.stock_frame,
                    text=threshold_text
                ).grid(row=i, column=4, padx=5, pady=5, sticky="w")
                
                # Status
                status_color = "#EF4444" if remaining <= threshold else "#10B981"
                status_text = "Low Stock" if remaining <= threshold else "OK"
                
                ctk.CTkLabel(
                    self.stock_frame,
                    text=status_text,
                    text_color=status_color,
                    font=("Helvetica", 12, "bold")
                ).grid(row=i, column=5, padx=5, pady=5, sticky="w")
                
                # Actions frame
                actions_frame = ctk.CTkFrame(self.stock_frame, fg_color="transparent")
                actions_frame.grid(row=i, column=6, padx=5, pady=5, sticky="w")
                
                # Add Stock button
                ctk.CTkButton(
                    actions_frame,
                    text="Add Stock",
                    command=lambda x=item_id: self.show_add_stock_dialog(x),
                    width=90,
                    height=30,
                    fg_color="#2563EB"
                ).pack(side="left", padx=5)
                
                # Delete button
                ctk.CTkButton(
                    actions_frame,
                    text="×",
                    command=lambda x=item_id: self.delete_item(x),
                    width=30,
                    height=30,
                    fg_color="#EF4444"
                ).pack(side="left", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stock data: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def show_add_dialog(self):
        """Show dialog to add new bar item"""
        dialog = AddBarItemDialog(self)
        dialog.grab_set()
    
    def show_add_stock_dialog(self, item_id):
        """Show dialog to add stock to existing item"""
        dialog = AddStockDialog(self, item_id)
        dialog.grab_set()
    
    def delete_item(self, item_id):
        """Delete bar item"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Get item name
            cursor.execute("SELECT item_name FROM bar_stock WHERE id = ?", (item_id,))
            item_name = cursor.fetchone()[0]
            
            if messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete {item_name}?"
            ):
                cursor.execute("DELETE FROM bar_stock WHERE id = ?", (item_id,))
                conn.commit()
                
                self.load_stock_data()
                messagebox.showinfo("Success", "Item deleted successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
        finally:
            if conn:
                conn.close()
