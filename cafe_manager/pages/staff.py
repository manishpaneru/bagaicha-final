"""
Staff page implementation for the Cafe Management System.
Handles staff management, salary tracking, and payment history.
"""

import customtkinter as ctk
from utils.constants import *
from database import DatabaseManager
from datetime import datetime
from tkinter import messagebox
import sqlite3
from tkcalendar import DateEntry

class AddStaffDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = DatabaseManager()
        
        # Window setup
        self.title("Add Staff Member")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Initialize variables
        self.staff_positions = ["Manager", "Waiter", "Chef", "Bartender", "Cleaner"]
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="Add New Staff Member",
            font=("Helvetica", 20, "bold")
        ).pack(pady=(0, 20))
        
        # Name Field
        ctk.CTkLabel(main_frame, text="Full Name:").pack(anchor="w", pady=(10, 0))
        self.name_entry = ctk.CTkEntry(main_frame, width=300)
        self.name_entry.pack(pady=(0, 10))
        
        # Position Selection
        ctk.CTkLabel(main_frame, text="Position:").pack(anchor="w", pady=(10, 0))
        self.position_var = ctk.StringVar(value=self.staff_positions[0])
        self.position_menu = ctk.CTkOptionMenu(
            main_frame,
            variable=self.position_var,
            values=self.staff_positions,
            width=300
        )
        self.position_menu.pack(pady=(0, 10))
        
        # Contact Number
        ctk.CTkLabel(main_frame, text="Contact Number:").pack(anchor="w", pady=(10, 0))
        self.contact_entry = ctk.CTkEntry(main_frame, width=300)
        self.contact_entry.pack(pady=(0, 10))
        
        # Salary Field
        ctk.CTkLabel(main_frame, text="Monthly Salary:").pack(anchor="w", pady=(10, 0))
        self.salary_entry = ctk.CTkEntry(main_frame, width=300)
        self.salary_entry.pack(pady=(0, 10))
        
        # Join Date
        ctk.CTkLabel(main_frame, text="Join Date:").pack(anchor="w", pady=(10, 0))
        self.date_entry = DateEntry(
            main_frame,
            width=30,
            background='darkblue',
            foreground='white',
            date_pattern='yyyy-mm-dd'
        )
        self.date_entry.pack(pady=(0, 20))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20)
        
        # Save Button
        self.save_button = ctk.CTkButton(
            buttons_frame,
            text="Save Staff",
            command=self.save_staff,
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
    
    def save_staff(self):
        """Save staff member to database"""
        try:
            # Get and validate inputs
            name = self.name_entry.get().strip()
            position = self.position_var.get()
            contact = self.contact_entry.get().strip()
            join_date = self.date_entry.get_date()
            
            try:
                salary = float(self.salary_entry.get())
                if salary <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid salary amount")
                return
            
            if not all([name, position, contact]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO staff (
                    name, title, contact, salary, 
                    join_date, is_active
                ) VALUES (?, ?, ?, ?, ?, 1)
            """, (name, position, contact, salary, join_date))
            
            conn.commit()
            messagebox.showinfo("Success", "Staff member added successfully!")
            
            # Refresh parent's staff list
            self.parent.load_staff_data()
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add staff member: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

class StaffPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = DatabaseManager()
        
        # Initialize variables
        self.staff_members = []
        
        # Configure grid weights for full width
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_staff_data()
    
    def setup_ui(self):
        # Header with Add Staff button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20,0), sticky="nsew")
        header_frame.grid_columnconfigure(0, weight=1)  # Give weight to title column
        
        # Title
        ctk.CTkLabel(
            header_frame,
            text="Staff Management",
            font=("Helvetica", 24, "bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Add Staff Button
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Add Staff",
            command=self.show_add_staff_dialog,
            width=150,
            height=40
        )
        add_btn.grid(row=0, column=1, sticky="e")
        
        # Staff Table
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.table_frame.grid_columnconfigure(tuple(range(8)), weight=1)  # Give equal weight to all columns
        self.table_frame.grid_rowconfigure(1, weight=1)  # Give weight to scrollable frame
        
        # Table Headers
        headers = ["Name", "Position", "Contact", "Salary", "Join Date", "Last Paid", "Status", "Actions"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=("Helvetica", 12, "bold")
            ).grid(row=0, column=col, padx=10, pady=5, sticky="ew")
        
        # Scrollable frame for staff list
        self.staff_frame = ctk.CTkScrollableFrame(self.table_frame)
        self.staff_frame.grid(row=1, column=0, columnspan=len(headers), sticky="nsew")
        
        # Configure scrollable frame columns
        for i in range(len(headers)):
            self.staff_frame.grid_columnconfigure(i, weight=1)
    
    def load_staff_data(self):
        """Load staff data from database"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, title, contact, salary, 
                       join_date, last_paid_date, is_active
                FROM staff
                ORDER BY name
            """)
            
            self.staff_members = cursor.fetchall()
            self.update_staff_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load staff data: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def update_staff_list(self):
        """Update staff list display"""
        # Clear current list
        for widget in self.staff_frame.winfo_children():
            widget.destroy()
        
        # Add staff members to list
        for row, staff in enumerate(self.staff_members):
            staff_id, name, title, contact, salary, join_date, last_paid, is_active = staff
            
            # Create a frame for this row
            row_frame = ctk.CTkFrame(self.staff_frame, fg_color="transparent")
            row_frame.grid(row=row, column=0, columnspan=8, sticky="ew", pady=2)
            
            # Configure row columns
            for i in range(8):
                row_frame.grid_columnconfigure(i, weight=1)
            
            # Add staff data
            cols = [name, title, contact, f"₹{salary:,.2f}", join_date, 
                   last_paid or "Never", "Active" if is_active else "Inactive"]
            
            for col, text in enumerate(cols):
                ctk.CTkLabel(
                    row_frame,
                    text=str(text)
                ).grid(row=0, column=col, padx=10, pady=5, sticky="ew")
            
            # Actions buttons
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=7, padx=10, pady=5, sticky="ew")
            
            if is_active:
                # Pay Salary button
                ctk.CTkButton(
                    actions_frame,
                    text="Pay Salary",
                    width=100,
                    command=lambda s=staff_id: self.record_payment(s)
                ).pack(side="left", padx=5)
            
            # Toggle Status button
            ctk.CTkButton(
                actions_frame,
                text="Deactivate" if is_active else "Activate",
                width=100,
                fg_color="#EF4444" if is_active else "#10B981",
                command=lambda s=staff_id, a=is_active: self.toggle_status(s, a)
            ).pack(side="left", padx=5)
    
    def show_add_staff_dialog(self):
        """Show dialog to add new staff member"""
        dialog = AddStaffDialog(self)
        dialog.grab_set()
    
    def record_payment(self, staff_id):
        """Record salary payment for staff member"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Get staff details
            cursor.execute("""
                SELECT name, salary FROM staff WHERE id = ?
            """, (staff_id,))
            
            staff = cursor.fetchone()
            if not staff:
                raise Exception("Staff member not found")
                
            name, salary = staff
            
            # Start transaction
            cursor.execute("BEGIN")
            
            # Record payment
            cursor.execute("""
                INSERT INTO staff_payments (
                    staff_id, amount, payment_date
                ) VALUES (?, ?, DATE('now', 'localtime'))
            """, (staff_id, salary))
            
            # Update last paid date
            cursor.execute("""
                UPDATE staff
                SET last_paid_date = DATE('now', 'localtime')
                WHERE id = ?
            """, (staff_id,))
            
            # Add to expenses
            cursor.execute("""
                INSERT INTO expenses (
                    name, title, category, quantity,
                    price_per_unit, total_price, expense_date
                ) VALUES (?, ?, ?, ?, ?, ?, DATE('now', 'localtime'))
            """, (name, "Salary Payment", "Management", 1, salary, salary))
            
            conn.commit()
            messagebox.showinfo("Success", f"Salary paid to {name}")
            
            self.load_staff_data()  # Refresh list
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to record payment: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def toggle_status(self, staff_id, current_status):
        """Toggle staff member's active status"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE staff
                SET is_active = ?
                WHERE id = ?
            """, (not current_status, staff_id))
            
            conn.commit()
            self.load_staff_data()  # Refresh list
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {str(e)}")
        finally:
            if conn:
                conn.close()
