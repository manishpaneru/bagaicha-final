"""
Sales page implementation for the Cafe Management System.
Handles table management and billing operations.
"""

import customtkinter as ctk
from utils.constants import *
from database import DatabaseManager
from datetime import datetime
import sqlite3
from tkinter import messagebox

class BillWindow(ctk.CTkToplevel):
    """Bill window for managing table orders."""
    
    def __init__(self, parent, table_number):
        super().__init__(parent)
        self.parent = parent
        self.table_number = table_number
        self.db = DatabaseManager()
        
        # Window setup
        self.title(f"Table {table_number} - Bill")
        self.geometry("800x600")
        self.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Initialize variables
        self.menu_items = {}
        self.bill_items = {}
        self.current_sale_id = None
        self.subtotal = 0.0
        self.total = 0.0
        
        # Initialize category menu variable
        self.category_menu = None
        self.selected_category = ctk.StringVar(value="All Categories")
        
        # Setup UI first
        self.setup_ui()
        
        # Then load menu items
        self.load_menu_items()
        
        # Finally load existing bill if any
        self.load_existing_bill()
    
    def setup_ui(self):
        # Split view - Menu items on left, Bill on right
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Menu items frame (Left)
        menu_frame = ctk.CTkFrame(self)
        menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Search and filter
        search_frame = ctk.CTkFrame(menu_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            search_frame,
            text="Search:",
            font=FONTS["body"]
        ).pack(side="left", padx=5)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_menu_items)
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS["body"],
            width=150
        )
        search_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            search_frame,
            text="Category:",
            font=FONTS["body"]
        ).pack(side="left", padx=5)
        
        self.category_menu = ctk.CTkOptionMenu(
            search_frame,
            values=["All Categories"],
            command=self.filter_by_category,
            font=FONTS["body"]
        )
        self.category_menu.pack(side="left", padx=5)
        
        # Menu items list
        self.menu_list = ctk.CTkScrollableFrame(menu_frame)
        self.menu_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bill frame (Right)
        self.bill_frame = ctk.CTkFrame(self)
        self.bill_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Bill title
        ctk.CTkLabel(
            self.bill_frame,
            text=f"Table {self.table_number} - Bill",
            font=FONTS["heading"]
        ).pack(pady=10)
        
        # Bill items list
        self.bill_list = ctk.CTkScrollableFrame(self.bill_frame)
        self.bill_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bill summary frame
        summary_frame = ctk.CTkFrame(self.bill_frame, fg_color="transparent")
        summary_frame.pack(fill="x", padx=20, pady=10)
        
        # Subtotal
        subtotal_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        subtotal_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(
            subtotal_frame,
            text="Subtotal:",
            font=FONTS["body"]
        ).pack(side="left")
        self.subtotal_label = ctk.CTkLabel(
            subtotal_frame,
            text="₹0.00",
            font=FONTS["body"]
        )
        self.subtotal_label.pack(side="right")
        
        # Discount
        discount_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        discount_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(
            discount_frame,
            text="Discount:",
            font=FONTS["body"]
        ).pack(side="left")
        
        self.discount_type = ctk.StringVar(value="percentage")
        self.discount_value = ctk.StringVar(value="0")
        
        discount_entry = ctk.CTkEntry(
            discount_frame,
            textvariable=self.discount_value,
            width=60,
            font=FONTS["body"]
        )
        discount_entry.pack(side="right", padx=5)
        
        self.discount_menu = ctk.CTkOptionMenu(
            discount_frame,
            values=["percentage", "amount"],
            variable=self.discount_type,
            width=100,
            font=FONTS["body"],
            command=self.update_total
        )
        self.discount_menu.pack(side="right", padx=5)
        
        # Bind discount value changes
        self.discount_value.trace("w", lambda *args: self.update_total())
        
        # Total
        total_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        total_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(
            total_frame,
            text="Total:",
            font=FONTS["subheading"]
        ).pack(side="left")
        self.total_label = ctk.CTkLabel(
            total_frame,
            text="₹0.00",
            font=FONTS["subheading"]
        )
        self.total_label.pack(side="right")
        
        # Add Pay Bill button at bottom
        self.pay_bill_button = ctk.CTkButton(
            self.bill_frame,
            text="Pay Bill",
            fg_color="#10B981",  # Green color
            hover_color="#059669",
            command=self.pay_bill,
            height=40,
            font=FONTS["body"]
        )
        self.pay_bill_button.pack(side="bottom", pady=20, padx=20, fill="x")
    
    def update_total(self, *args):
        """Update bill total based on discount"""
        try:
            discount_value = float(self.discount_value.get() or 0)
            if self.discount_type.get() == "percentage":
                if discount_value > 100:
                    discount_value = 100
                discount_amount = self.subtotal * (discount_value / 100)
            else:
                if discount_value > self.subtotal:
                    discount_value = self.subtotal
                discount_amount = discount_value
            
            self.total = self.subtotal - discount_amount
            self.total_label.configure(text=f"₹{self.total:.2f}")
            
        except ValueError:
            # Invalid discount value, reset to 0
            self.discount_value.set("0")
            self.total = self.subtotal
            self.total_label.configure(text=f"₹{self.total:.2f}")
    
    def load_menu_items(self):
        """Load all menu items from database"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Get menu items with categories
            cursor.execute("""
                SELECT m.id, m.name, c.name, m.price
                FROM menu_items m
                JOIN menu_categories c ON m.category_id = c.id
                ORDER BY c.name, m.name
            """)
            
            items = cursor.fetchall()
            
            # Organize by category
            categories = {}
            for item in items:
                if item[2] not in categories:
                    categories[item[2]] = []
                categories[item[2]].append({
                    'id': item[0],
                    'name': item[1],
                    'price': item[3]
                })
            
            self.menu_items = categories
            
            # Update category menu
            self.category_menu.configure(
                values=["All Categories"] + list(categories.keys())
            )
            
            # Display items
            self.display_menu_items()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load menu items: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def display_menu_items(self, category=None, search_text=None):
        """Display menu items in the menu list"""
        # Clear existing items
        for widget in self.menu_list.winfo_children():
            widget.destroy()
        
        # Display items
        row = 0
        for cat, items in self.menu_items.items():
            if category and category != "All Categories" and cat != category:
                continue
            
            # Category header
            ctk.CTkLabel(
                self.menu_list,
                text=cat,
                font=FONTS["subheading"]
            ).grid(row=row, column=0, columnspan=3, padx=10, pady=(10,5), sticky="w")
            row += 1
            
            # Items
            for item in items:
                if search_text and search_text.lower() not in item['name'].lower():
                    continue
                
                # Item frame
                item_frame = ctk.CTkFrame(self.menu_list, fg_color="transparent")
                item_frame.grid(row=row, column=0, columnspan=3, padx=10, pady=2, sticky="ew")
                
                # Item name
                ctk.CTkLabel(
                    item_frame,
                    text=item['name'],
                    font=FONTS["body"]
                ).pack(side="left", padx=5)
                
                # Price
                ctk.CTkLabel(
                    item_frame,
                    text=f"₹{item['price']:.2f}",
                    font=FONTS["body"]
                ).pack(side="left", padx=5)
                
                # Add button
                ctk.CTkButton(
                    item_frame,
                    text="+",
                    width=30,
                    command=lambda i=item: self.add_to_bill(i)
                ).pack(side="right", padx=5)
                
                row += 1
    
    def filter_menu_items(self, *args):
        """Filter menu items based on search text and category"""
        search_text = self.search_var.get()
        category = self.category_menu.get()
        self.display_menu_items(category, search_text)
    
    def filter_by_category(self, category):
        """Filter menu items by category"""
        self.display_menu_items(category, self.search_var.get())
    
    def add_to_bill(self, item):
        """Add item to bill"""
        if item['id'] in self.bill_items:
            self.bill_items[item['id']]['quantity'] += 1
        else:
            self.bill_items[item['id']] = {
                'name': item['name'],
                'price': item['price'],
                'quantity': 1
            }
        
        self.update_bill_display()
    
    def update_bill_display(self):
        """Update the bill display"""
        # Clear existing items
        for widget in self.bill_list.winfo_children():
            widget.destroy()
        
        # Display items
        self.subtotal = 0
        for item_id, item in self.bill_items.items():
            # Item frame
            item_frame = ctk.CTkFrame(self.bill_list, fg_color="transparent")
            item_frame.pack(fill="x", padx=10, pady=2)
            
            # Item name and quantity
            ctk.CTkLabel(
                item_frame,
                text=f"{item['name']} x{item['quantity']}",
                font=FONTS["body"]
            ).pack(side="left", padx=5)
            
            # Total price
            total = item['price'] * item['quantity']
            self.subtotal += total
            ctk.CTkLabel(
                item_frame,
                text=f"₹{total:.2f}",
                font=FONTS["body"]
            ).pack(side="right", padx=5)
            
            # Remove button
            ctk.CTkButton(
                item_frame,
                text="-",
                width=30,
                command=lambda i=item_id: self.remove_from_bill(i)
            ).pack(side="right", padx=5)
        
        # Update totals
        self.subtotal_label.configure(text=f"₹{self.subtotal:.2f}")
        self.update_total()
    
    def remove_from_bill(self, item_id):
        """Remove item from bill"""
        if item_id in self.bill_items:
            if self.bill_items[item_id]['quantity'] > 1:
                self.bill_items[item_id]['quantity'] -= 1
            else:
                del self.bill_items[item_id]
            
            self.update_bill_display()
    
    def load_existing_bill(self):
        """Load existing bill for the table if any"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Get pending sale for the table
            cursor.execute("""
                SELECT id, subtotal, discount_type, discount_value, total_amount
                FROM sales
                WHERE table_number = ? AND payment_status = 'pending'
                ORDER BY created_at DESC
                LIMIT 1
            """, (self.table_number,))
            
            sale = cursor.fetchone()
            if sale:
                self.current_sale_id = sale[0]
                
                # Get sale items
                cursor.execute("""
                    SELECT menu_item_id, quantity, price_per_unit
                    FROM sale_items
                    WHERE sale_id = ?
                """, (self.current_sale_id,))
                
                items = cursor.fetchall()
                for item in items:
                    # Get item name
                    cursor.execute("""
                        SELECT name
                        FROM menu_items
                        WHERE id = ?
                    """, (item[0],))
                    name = cursor.fetchone()[0]
                    
                    self.bill_items[item[0]] = {
                        'name': name,
                        'price': item[2],
                        'quantity': item[1]
                    }
                
                # Set discount
                self.discount_type.set(sale[2] or "percentage")
                self.discount_value.set(str(sale[3] or 0))
                
                # Update display
                self.update_bill_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load existing bill: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def save_bill(self):
        """Save current bill to database"""
        if not self.bill_items:
            messagebox.showerror("Error", "Cannot save empty bill")
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN")
            
            if self.current_sale_id:
                # Update existing sale
                cursor.execute("""
                    UPDATE sales
                    SET subtotal = ?, discount_type = ?, discount_value = ?, total_amount = ?
                    WHERE id = ?
                """, (
                    self.subtotal,
                    self.discount_type.get(),
                    float(self.discount_value.get() or 0),
                    self.total,
                    self.current_sale_id
                ))
                
                # Delete existing items
                cursor.execute("DELETE FROM sale_items WHERE sale_id = ?", (self.current_sale_id,))
            else:
                # Create new sale
                cursor.execute("""
                    INSERT INTO sales (
                        table_number, subtotal, discount_type,
                        discount_value, total_amount, payment_status
                    ) VALUES (?, ?, ?, ?, ?, 'pending')
                """, (
                    self.table_number,
                    self.subtotal,
                    self.discount_type.get(),
                    float(self.discount_value.get() or 0),
                    self.total
                ))
                
                self.current_sale_id = cursor.lastrowid
                
                # Update table status
                cursor.execute("""
                    UPDATE tables
                    SET status = 'occupied'
                    WHERE table_number = ?
                """, (self.table_number,))
            
            # Insert sale items
            for item_id, item in self.bill_items.items():
                cursor.execute("""
                    INSERT INTO sale_items (
                        sale_id, menu_item_id, quantity,
                        price_per_unit, total_price
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    self.current_sale_id,
                    item_id,
                    item['quantity'],
                    item['price'],
                    item['price'] * item['quantity']
                ))
            
            # Commit transaction
            conn.commit()
            
            # Update parent's table button
            self.parent.update_table_status(self.table_number, "occupied")
            
        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Error", f"Failed to save bill: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def pay_bill(self):
        """Handle bill payment and table status update"""
        if not self.current_sale_id:
            messagebox.showerror("Error", "Please save the bill first")
            return
            
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN")
            
            # Update table status to vacant
            cursor.execute("""
                UPDATE tables
                SET status = 'vacant'
                WHERE table_number = ?
            """, (self.table_number,))
            
            # Update sale status to completed
            cursor.execute("""
                UPDATE sales
                SET payment_status = 'completed'
                WHERE id = ?
            """, (self.current_sale_id,))
            
            # Commit transaction
            conn.commit()
            
            # Update parent's table button
            self.parent.update_table_status(self.table_number, "vacant")
            
            # Close bill window
            self.destroy()
            
        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Error", f"Failed to process payment: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class SalesPage(ctk.CTkFrame):
    """Sales page showing table grid and managing bills."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Initialize variables
        self.db = DatabaseManager()
        self.table_buttons = {}
        self.active_bills = {}
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_table_status()
        
        # Start auto-refresh
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Create and arrange all UI components."""
        # Configure grid
        for i in range(5):
            self.grid_columnconfigure(i, weight=1)
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
        
        # Create table grid
        self.create_table_grid()
    
    def create_table_grid(self):
        """Create 5x3 grid of table buttons."""
        for i in range(15):
            row = i // 5
            col = i % 5
            
            button = self.create_table_button(i + 1)
            button.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.table_buttons[i + 1] = button
    
    def create_table_button(self, number):
        """Create individual table button."""
        return ctk.CTkButton(
            self,
            text=f"Table {number}",
            fg_color="white",
            text_color="black",
            hover_color="#E5E7EB",
            height=120,
            width=120,
            corner_radius=10,
            command=lambda: self.open_bill(number)
        )
    
    def load_table_status(self):
        """Load current status of all tables."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT table_number, status
                FROM tables
                ORDER BY table_number
            """)
            
            for table_number, status in cursor.fetchall():
                self.update_table_status(table_number, status)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table status: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def update_table_status(self, table_number, status):
        """Update table status and appearance."""
        button = self.table_buttons.get(table_number)
        if button:
            if status == "occupied":
                button.configure(
                    fg_color="#10B981",  # Green
                    text_color="white",
                    hover_color="#059669"
                )
            else:
                button.configure(
                    fg_color="white",
                    text_color="black",
                    hover_color="#E5E7EB"
                )
    
    def open_bill(self, table_number):
        """Open bill window for a table."""
        if table_number in self.active_bills:
            self.active_bills[table_number].focus()
        else:
            bill_window = BillWindow(self, table_number)
            self.active_bills[table_number] = bill_window
            
            # Remove from active bills when closed
            def on_close():
                del self.active_bills[table_number]
                bill_window.destroy()
            
            bill_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        self.load_table_status()
        self.after(30000, self.start_auto_refresh)  # Refresh every 30 seconds
