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
import os

class BillPreviewWindow(ctk.CTkToplevel):
    def __init__(self, parent, table_number, bill_items, subtotal, discount_type, discount_value, total):
        super().__init__(parent)
        self.title(f"Bill Preview - Table {table_number}")
        self.geometry("400x600")
        self.resizable(False, False)
        
        # Store data
        self.table_number = table_number
        self.bill_items = bill_items
        self.subtotal = subtotal
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.total = total
        
        # Define fonts directly
        self.header_font = ("Helvetica", 20, "bold")
        self.subheader_font = ("Helvetica", 14, "bold")
        self.body_font = ("Helvetica", 12)
        self.body_bold_font = ("Helvetica", 12, "bold")
        
        # Center window
        self.center_window()
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="TROPICAL BAGAICHA",
            font=self.header_font
        ).pack()
        
        ctk.CTkLabel(
            header_frame,
            text="Restaurant & Bar",
            font=self.body_font
        ).pack()
        
        ctk.CTkLabel(
            header_frame,
            text=f"Table: {self.table_number}",
            font=self.subheader_font
        ).pack()
        
        ctk.CTkLabel(
            header_frame,
            text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            font=self.body_font
        ).pack()
        
        # Items list
        items_frame = ctk.CTkScrollableFrame(self.main_frame)
        items_frame.pack(fill="both", expand=True, pady=10)
        
        # Headers
        headers_frame = ctk.CTkFrame(items_frame, fg_color="transparent")
        headers_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(headers_frame, text="Item", font=self.body_bold_font).pack(side="left", expand=True, anchor="w")
        ctk.CTkLabel(headers_frame, text="Qty", font=self.body_bold_font).pack(side="left", padx=10)
        ctk.CTkLabel(headers_frame, text="Price", font=self.body_bold_font).pack(side="left", padx=10)
        ctk.CTkLabel(headers_frame, text="Total", font=self.body_bold_font).pack(side="right")
        
        # List items
        for item_id, item in self.bill_items.items():
            item_frame = ctk.CTkFrame(items_frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=5, pady=2)
            
            ctk.CTkLabel(
                item_frame,
                text=item["name"],
                font=self.body_font
            ).pack(side="left", expand=True, anchor="w")
            
            ctk.CTkLabel(
                item_frame,
                text=str(item["quantity"]),
                font=self.body_font
            ).pack(side="left", padx=10)
            
            ctk.CTkLabel(
                item_frame,
                text=f"₹{item['price']:.2f}",
                font=self.body_font
            ).pack(side="left", padx=10)
            
            ctk.CTkLabel(
                item_frame,
                text=f"₹{item['price'] * item['quantity']:.2f}",
                font=self.body_font
            ).pack(side="right")
        
        # Totals
        totals_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        totals_frame.pack(fill="x", pady=10)
        
        # Subtotal
        subtotal_frame = ctk.CTkFrame(totals_frame, fg_color="transparent")
        subtotal_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(
            subtotal_frame,
            text="Subtotal:",
            font=self.body_font
        ).pack(side="left")
        ctk.CTkLabel(
            subtotal_frame,
            text=f"₹{self.subtotal:.2f}",
            font=self.body_font
        ).pack(side="right")
        
        # Discount
        if float(self.discount_value or 0) > 0:
            discount_frame = ctk.CTkFrame(totals_frame, fg_color="transparent")
            discount_frame.pack(fill="x", pady=2)
            
            discount_text = f"Discount ({self.discount_type}):"
            if self.discount_type == "percentage":
                discount_text = f"Discount ({self.discount_value}%):"
            
            ctk.CTkLabel(
                discount_frame,
                text=discount_text,
                font=self.body_font
            ).pack(side="left")
            
            discount_amount = float(self.discount_value or 0)
            if self.discount_type == "percentage":
                discount_amount = self.subtotal * (float(self.discount_value or 0) / 100)
            
            ctk.CTkLabel(
                discount_frame,
                text=f"₹{discount_amount:.2f}",
                font=self.body_font
            ).pack(side="right")
        
        # Total
        total_frame = ctk.CTkFrame(totals_frame, fg_color="transparent")
        total_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(
            total_frame,
            text="Total:",
            font=self.subheader_font
        ).pack(side="left")
        ctk.CTkLabel(
            total_frame,
            text=f"₹{self.total:.2f}",
            font=self.subheader_font
        ).pack(side="right")
        
        # Save Button
        self.save_btn = ctk.CTkButton(
            self.main_frame,
            text="Save Bill",
            command=self.save_bill_as_image,
            font=self.body_font,
            fg_color="#2563EB",  # Blue color
            hover_color="#1D4ED8"
        )
        self.save_btn.pack(pady=10)
    
    def save_bill_as_image(self):
        try:
            # Create filename with datetime
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            filename = f"bill-{timestamp}-table{self.table_number}.png"
            
            # Get widget position and size
            x = self.main_frame.winfo_rootx()
            y = self.main_frame.winfo_rooty()
            width = self.main_frame.winfo_width()
            height = self.main_frame.winfo_height()
            
            # Take screenshot
            from PIL import ImageGrab
            screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
            
            # Create bills directory if it doesn't exist
            os.makedirs('bills', exist_ok=True)
            
            # Save image
            filepath = os.path.join('bills', filename)
            screenshot.save(filepath)
            
            messagebox.showinfo("Success", f"Bill saved as {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bill: {str(e)}")
    
    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

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
        self.subtotal = 0.0
        self.total = 0.0
        
        # Initialize category menu variable
        self.category_menu = None
        self.selected_category = ctk.StringVar(value="All Categories")
        
        # Setup UI first
        self.setup_ui()
        
        # Then load menu items
        self.load_menu_items()
        
        # Load existing temporary bill items
        self.load_existing_items()
    
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
        
        # Add Show Bill Preview button
        self.show_bill_btn = ctk.CTkButton(
            self.bill_frame,
            text="Show Bill Preview",
            command=self.show_bill_preview,
            font=FONTS["body"],
            fg_color="#6366F1",  # Indigo color
            hover_color="#4F46E5"
        )
        self.show_bill_btn.pack(side="bottom", pady=(10,0), padx=20, fill="x")
        
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
        self.pay_bill_button.pack(side="bottom", pady=10, padx=20, fill="x")
    
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
        """Add item to bill with quantity selection"""
        # Create quantity input dialog
        quantity_dialog = ctk.CTkInputDialog(
            text="Enter quantity:",
            title="Quantity"
        )
        quantity = quantity_dialog.get_input()
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Please enter a valid quantity")
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN")
            
            # Add item with quantity
            if item['id'] in self.bill_items:
                new_quantity = self.bill_items[item['id']]['quantity'] + quantity
                total_price = item['price'] * new_quantity
                
                # Update temporary_bills
                cursor.execute("""
                    UPDATE temporary_bills
                    SET quantity = ?, total_price = ?
                    WHERE table_number = ? AND menu_item_id = ?
                """, (new_quantity, total_price, self.table_number, item['id']))
                
                self.bill_items[item['id']]['quantity'] = new_quantity
            else:
                total_price = item['price'] * quantity
                
                # Insert into temporary_bills
                cursor.execute("""
                    INSERT INTO temporary_bills (
                        table_number, menu_item_id, quantity,
                        price_per_unit, total_price
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    self.table_number,
                    item['id'],
                    quantity,
                    item['price'],
                    total_price
                ))
                
                self.bill_items[item['id']] = {
                    'name': item['name'],
                    'price': item['price'],
                    'quantity': quantity
                }
            
            # Update table status if this is the first item
            if len(self.bill_items) == 1:
                cursor.execute("""
                    UPDATE tables 
                    SET status = 'occupied'
                    WHERE table_number = ?
                """, (self.table_number,))
                
                # Update table button color in parent
                self.parent.update_table_status(self.table_number, "occupied")
            
            # Commit transaction
            conn.commit()
            
            # Update display
            self.update_bill_display()
            
        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")
        finally:
            if conn:
                conn.close()
    
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
            try:
                conn = self.db.connect()
                cursor = conn.cursor()
                
                # Start transaction
                cursor.execute("BEGIN")
                
                if self.bill_items[item_id]['quantity'] > 1:
                    # Update quantity
                    new_quantity = self.bill_items[item_id]['quantity'] - 1
                    total_price = self.bill_items[item_id]['price'] * new_quantity
                    
                    cursor.execute("""
                        UPDATE temporary_bills
                        SET quantity = ?, total_price = ?
                        WHERE table_number = ? AND menu_item_id = ?
                    """, (new_quantity, total_price, self.table_number, item_id))
                    
                    self.bill_items[item_id]['quantity'] = new_quantity
                else:
                    # Remove item completely
                    cursor.execute("""
                        DELETE FROM temporary_bills
                        WHERE table_number = ? AND menu_item_id = ?
                    """, (self.table_number, item_id))
                    
                    del self.bill_items[item_id]
                
                # If no items left, update table status
                if not self.bill_items:
                    cursor.execute("""
                        UPDATE tables
                        SET status = 'vacant'
                        WHERE table_number = ?
                    """, (self.table_number,))
                    self.parent.update_table_status(self.table_number, "vacant")
                
                # Commit transaction
                conn.commit()
                
                # Update display
                self.update_bill_display()
                
            except Exception as e:
                if conn:
                    conn.rollback()
                messagebox.showerror("Error", f"Failed to remove item: {str(e)}")
            finally:
                if conn:
                    conn.close()
    
    def load_existing_items(self):
        """Load any existing items for this table from temporary_bills"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tb.menu_item_id, mi.name, tb.quantity, 
                       tb.price_per_unit, tb.total_price
                FROM temporary_bills tb
                JOIN menu_items mi ON tb.menu_item_id = mi.id
                WHERE tb.table_number = ?
            """, (self.table_number,))
            
            existing_items = cursor.fetchall()
            
            for item in existing_items:
                self.bill_items[item[0]] = {
                    'name': item[1],
                    'quantity': item[2],
                    'price': item[3]
                }
            
            if self.bill_items:
                self.update_bill_display()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load existing items: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def pay_bill(self):
        """Handle bill payment"""
        if not self.bill_items:
            messagebox.showerror("Error", "Cannot process empty bill")
            return
            
        try:
            # First save the sale in database
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN")
            
            # Insert sale record
            cursor.execute("""
                INSERT INTO sales (
                    table_number, subtotal, discount_type,
                    discount_value, total_amount, payment_status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.table_number,
                self.subtotal,
                self.discount_type.get(),
                float(self.discount_value.get() or 0),
                self.total,
                "completed"
            ))
            
            sale_id = cursor.lastrowid
            
            # Insert sale items
            for item_id, item in self.bill_items.items():
                cursor.execute("""
                    INSERT INTO sale_items (
                        sale_id, menu_item_id, quantity,
                        price_per_unit, total_price
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    sale_id,
                    item_id,
                    item['quantity'],
                    item['price'],
                    item['price'] * item['quantity']
                ))
            
            # Clear temporary items
            cursor.execute("""
                DELETE FROM temporary_bills
                WHERE table_number = ?
            """, (self.table_number,))
            
            # Update table status back to vacant
            cursor.execute("""
                UPDATE tables
                SET status = 'vacant'
                WHERE table_number = ?
            """, (self.table_number,))
            
            # Commit transaction
            conn.commit()
            
            # Update table button color in parent
            self.parent.update_table_status(self.table_number, "vacant")
            
            # Show success message
            messagebox.showinfo("Success", "Payment processed successfully!")
            
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
    
    def show_bill_preview(self):
        """Show bill preview window"""
        if not self.bill_items:
            messagebox.showerror("Error", "No items in bill")
            return
        
        preview = BillPreviewWindow(
            self,
            self.table_number,
            self.bill_items,
            self.subtotal,
            self.discount_type.get(),
            self.discount_value.get(),
            self.total
        )
        preview.grab_set()  # Make dialog modal

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
