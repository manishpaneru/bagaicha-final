"""
Menu page implementation for the Cafe Management System.
Handles menu items and categories management.
"""

import customtkinter as ctk
from utils.constants import *
from database import DatabaseManager
from tkinter import messagebox
import sqlite3

class CategoryDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Window setup
        self.title("Add Category")
        self.geometry("300x150")
        self.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # UI Elements
        ctk.CTkLabel(self, text="Category Name:", font=FONTS["body"]).pack(pady=(20,5))
        self.name_entry = ctk.CTkEntry(self, width=200)
        self.name_entry.pack(pady=5)
        self.name_entry.focus()
        
        ctk.CTkButton(
            self,
            text="Save",
            command=self.save_category,
            font=FONTS["body"]
        ).pack(pady=20)
    
    def center_window(self):
        """Center the dialog window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def save_category(self):
        """Save new category to database"""
        try:
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a category name")
                return
                
            conn = self.parent.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO menu_categories (name)
                VALUES (?)
            """, (name,))
            
            conn.commit()
            
            # Refresh parent's category list
            self.parent.load_categories()
            self.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Category already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save category: {str(e)}")
        finally:
            if conn:
                conn.close()

class MenuItemDialog(ctk.CTkToplevel):
    def __init__(self, parent, categories, item=None):
        super().__init__(parent)
        self.parent = parent
        self.item = item
        self.categories = categories
        
        # Window setup
        self.title("Add Menu Item" if not item else "Edit Menu Item")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Center window
        self.center_window()
        
        self.setup_ui()
    
    def center_window(self):
        """Center the dialog window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        # Name Entry
        ctk.CTkLabel(self, text="Item Name:", font=FONTS["body"]).pack(pady=(20,5))
        self.name_entry = ctk.CTkEntry(self, width=250)
        self.name_entry.pack(pady=5)
        
        # Category Selection
        ctk.CTkLabel(self, text="Category:", font=FONTS["body"]).pack(pady=(10,5))
        self.category_var = ctk.StringVar()
        self.category_menu = ctk.CTkOptionMenu(
            self,
            variable=self.category_var,
            values=[cat[1] for cat in self.categories],
            font=FONTS["body"]
        )
        self.category_menu.pack(pady=5)
        
        # Price Entry
        ctk.CTkLabel(self, text="Price:", font=FONTS["body"]).pack(pady=(10,5))
        self.price_entry = ctk.CTkEntry(self, width=250)
        self.price_entry.pack(pady=5)
        
        # Fill data if editing
        if self.item:
            self.name_entry.insert(0, self.item[1])
            self.category_var.set(self.item[2])
            self.price_entry.insert(0, str(self.item[3]))
        else:
            # Set default category if available
            if self.categories:
                self.category_var.set(self.categories[0][1])
        
        # Save Button
        ctk.CTkButton(
            self,
            text="Save Item",
            command=self.save_item,
            font=FONTS["body"]
        ).pack(pady=20)
        
        # Focus on name entry
        self.name_entry.focus()
    
    def save_item(self):
        """Save menu item to database"""
        try:
            # Get and validate inputs
            name = self.name_entry.get().strip()
            category = self.category_var.get()
            price = self.price_entry.get().strip()
            
            # Validation
            if not all([name, category, price]):
                messagebox.showerror("Error", "Please fill all fields")
                return
                
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid price")
                return
                
            # Get category ID
            conn = self.parent.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM menu_categories WHERE name = ?", (category,))
            category_id = cursor.fetchone()[0]
            
            # Save or update item
            if self.item:  # Editing existing item
                cursor.execute("""
                    UPDATE menu_items
                    SET name = ?, category_id = ?, price = ?
                    WHERE id = ?
                """, (name, category_id, price, self.item[0]))
            else:  # Adding new item
                cursor.execute("""
                    INSERT INTO menu_items (name, category_id, price)
                    VALUES (?, ?, ?)
                """, (name, category_id, price))
            
            conn.commit()
            
            # Refresh parent's menu list
            self.parent.load_menu_items()
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save menu item: {str(e)}")
        finally:
            if conn:
                conn.close()

class MenuPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = DatabaseManager()
        
        # Initialize variables
        self.menu_items = []
        self.categories = []
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_categories()
        self.load_menu_items()
    
    def setup_ui(self):
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header Frame with Add Buttons
        self.create_header()
        
        # Menu Table Frame
        self.create_menu_table()
    
    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20,0), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Category Management
        self.category_menu = ctk.CTkOptionMenu(
            header_frame,
            values=["All Categories"],
            command=self.filter_by_category,
            font=FONTS["body"]
        )
        self.category_menu.grid(row=0, column=0, padx=10)
        
        # Buttons Frame
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="e")
        
        # Add Category Button
        ctk.CTkButton(
            buttons_frame,
            text="+ Add Category",
            width=120,
            command=self.show_category_dialog,
            font=FONTS["body"]
        ).pack(side="left", padx=5)
        
        # Add Menu Item Button
        ctk.CTkButton(
            buttons_frame,
            text="+ Add Menu Item",
            width=120,
            command=self.show_menu_item_dialog,
            font=FONTS["body"]
        ).pack(side="left", padx=5)
    
    def create_menu_table(self):
        # Table container
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.table_frame.grid_columnconfigure(2, weight=1)
        
        # Headers
        headers = ["Item Name", "Category", "Price", "Actions"]
        for col, text in enumerate(headers):
            ctk.CTkLabel(
                self.table_frame,
                text=text,
                font=FONTS["body"]
            ).grid(row=0, column=col, padx=10, pady=5, sticky="w")
        
        # Scrollable frame for menu items
        self.menu_frame = ctk.CTkScrollableFrame(self.table_frame)
        self.menu_frame.grid(row=1, column=0, columnspan=len(headers),
                           sticky="nsew", padx=5, pady=5)
        self.menu_frame.grid_columnconfigure(2, weight=1)
    
    def load_categories(self):
        """Load menu categories"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name FROM menu_categories ORDER BY name")
            self.categories = cursor.fetchall()
            
            # Update category dropdown
            category_names = ["All Categories"] + [cat[1] for cat in self.categories]
            self.category_menu.configure(values=category_names)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def load_menu_items(self, category_id=None):
        """Load menu items"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            if category_id:
                query = """
                    SELECT m.id, m.name, c.name, m.price, m.category_id
                    FROM menu_items m
                    JOIN menu_categories c ON m.category_id = c.id
                    WHERE m.category_id = ?
                    ORDER BY m.name
                """
                cursor.execute(query, (category_id,))
            else:
                query = """
                    SELECT m.id, m.name, c.name, m.price, m.category_id
                    FROM menu_items m
                    JOIN menu_categories c ON m.category_id = c.id
                    ORDER BY m.name
                """
                cursor.execute(query)
            
            self.menu_items = cursor.fetchall()
            self.update_menu_table()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load menu items: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def update_menu_table(self):
        """Update menu items display"""
        # Clear existing items
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
        
        # Add menu items
        for row, item in enumerate(self.menu_items):
            # Item name
            ctk.CTkLabel(
                self.menu_frame,
                text=item[1],
                font=FONTS["body"]
            ).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            
            # Category
            ctk.CTkLabel(
                self.menu_frame,
                text=item[2],
                font=FONTS["body"]
            ).grid(row=row, column=1, padx=10, pady=5, sticky="w")
            
            # Price
            ctk.CTkLabel(
                self.menu_frame,
                text=f"₹{item[3]:.2f}",
                font=FONTS["body"]
            ).grid(row=row, column=2, padx=10, pady=5, sticky="w")
            
            # Actions Frame
            actions_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
            actions_frame.grid(row=row, column=3, padx=10, pady=5, sticky="e")
            
            # Edit button
            ctk.CTkButton(
                actions_frame,
                text="Edit",
                width=60,
                command=lambda i=item: self.show_menu_item_dialog(i),
                font=FONTS["body"]
            ).pack(side="left", padx=2)
            
            # Delete button
            ctk.CTkButton(
                actions_frame,
                text="Delete",
                width=60,
                fg_color="red",
                hover_color="darkred",
                command=lambda i=item: self.delete_menu_item(i[0]),
                font=FONTS["body"]
            ).pack(side="left", padx=2)
    
    def filter_by_category(self, category_name):
        """Filter menu items by category"""
        if category_name == "All Categories":
            self.load_menu_items()
        else:
            # Find category ID
            category_id = None
            for cat in self.categories:
                if cat[1] == category_name:
                    category_id = cat[0]
                    break
            
            if category_id:
                self.load_menu_items(category_id)
    
    def show_category_dialog(self):
        """Show dialog to add new category"""
        dialog = CategoryDialog(self)
        dialog.grab_set()  # Make dialog modal
    
    def show_menu_item_dialog(self, item=None):
        """Show dialog to add/edit menu item"""
        if not self.categories:
            messagebox.showerror("Error", "Please add a category first")
            return
        dialog = MenuItemDialog(self, self.categories, item)
        dialog.grab_set()  # Make dialog modal
    
    def add_category(self, name):
        """Add new category"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO menu_categories (name)
                VALUES (?)
            """, (name,))
            
            conn.commit()
            self.load_categories()
            
        except Exception as e:
            raise e
        finally:
            if conn:
                conn.close()
    
    def add_menu_item(self, name, category_id, price):
        """Add new menu item"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO menu_items (name, category_id, price)
                VALUES (?, ?, ?)
            """, (name, category_id, price))
            
            conn.commit()
            self.load_menu_items()
            
        except Exception as e:
            raise e
        finally:
            if conn:
                conn.close()
    
    def edit_menu_item(self, item_id, name, category_id, price):
        """Edit existing menu item"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE menu_items
                SET name = ?, category_id = ?, price = ?
                WHERE id = ?
            """, (name, category_id, price, item_id))
            
            conn.commit()
            self.load_menu_items()
            
        except Exception as e:
            raise e
        finally:
            if conn:
                conn.close()
    
    def delete_menu_item(self, item_id):
        """Delete menu item"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            try:
                conn = self.db.connect()
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
                conn.commit()
                
                self.load_menu_items()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete menu item: {str(e)}")
            finally:
                if conn:
                    conn.close()
