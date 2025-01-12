"""
Staff page implementation for the Cafe Management System.
Handles staff management, salary tracking, and payment history.
"""

import customtkinter as ctk
from utils.constants import *
from database import DatabaseManager
from datetime import datetime, date
from tkinter import messagebox
import sqlite3

class PaymentDialog(ctk.CTkToplevel):
    """Dialog for recording staff payments."""
    
    def __init__(self, parent, staff_id, staff_name, salary):
        super().__init__(parent)
        self.parent = parent
        self.staff_id = staff_id
        self.default_amount = salary
        
        # Window setup
        self.title(f"Record Payment - {staff_name}")
        self.geometry("300x200")
        self.resizable(False, False)
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Create and arrange UI components."""
        # Amount entry
        ctk.CTkLabel(self, text="Payment Amount:").pack(pady=(20,5))
        
        self.amount_entry = ctk.CTkEntry(self)
        self.amount_entry.insert(0, str(self.default_amount))
        self.amount_entry.pack(pady=5)
        
        # Confirm button
        ctk.CTkButton(
            self,
            text="Confirm Payment",
            command=self.confirm_payment
        ).pack(pady=20)
    
    def confirm_payment(self):
        """Validate and confirm the payment."""
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
            
            self.parent.record_payment(self.staff_id, amount)
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

class AddStaffDialog(ctk.CTkToplevel):
    """Dialog for adding new staff members."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Window setup
        self.title("Add Staff Member")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Create and arrange UI components."""
        # Name entry
        ctk.CTkLabel(self, text="Name:").pack(pady=(20,5))
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.pack(pady=5)
        
        # Title entry
        ctk.CTkLabel(self, text="Title:").pack(pady=(10,5))
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.pack(pady=5)
        
        # Contact entry
        ctk.CTkLabel(self, text="Contact:").pack(pady=(10,5))
        self.contact_entry = ctk.CTkEntry(self)
        self.contact_entry.pack(pady=5)
        
        # Salary entry
        ctk.CTkLabel(self, text="Salary:").pack(pady=(10,5))
        self.salary_entry = ctk.CTkEntry(self)
        self.salary_entry.pack(pady=5)
        
        # Join date (defaults to today)
        ctk.CTkLabel(self, text="Join Date:").pack(pady=(10,5))
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.date_entry.pack(pady=5)
        
        # Save button
        ctk.CTkButton(
            self,
            text="Add Staff Member",
            command=self.save_staff
        ).pack(pady=20)
    
    def save_staff(self):
        """Validate and save the new staff member."""
        try:
            name = self.name_entry.get().strip()
            title = self.title_entry.get().strip()
            contact = self.contact_entry.get().strip()
            salary = float(self.salary_entry.get())
            join_date = self.date_entry.get()
            
            if not all([name, title, contact]):
                raise ValueError("Please fill in all fields")
            if salary <= 0:
                raise ValueError("Salary must be greater than 0")
            
            # Validate date format
            try:
                datetime.strptime(join_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
            
            self.parent.add_staff(name, title, contact, salary, join_date)
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

class StaffPage(ctk.CTkFrame):
    """Staff page showing staff management and payment tracking."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = DatabaseManager()
        
        # Initialize variables
        self.staff_members = []
        self.current_month = datetime.now().strftime("%Y-%m")
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_staff_data()
    
    def setup_ui(self):
        """Create and arrange all UI components."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create header with Add Staff button
        self.create_header()
        
        # Create staff table
        self.create_staff_table()
        
        # Create payment history section
        self.create_payment_section()
    
    def create_header(self):
        """Create page header with Add Staff button."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20,0), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        ctk.CTkLabel(
            header_frame,
            text="Staff Management",
            font=FONTS["heading"]
        ).grid(row=0, column=0, padx=10, sticky="w")
        
        # Add Staff Button
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Add Staff",
            command=self.show_add_staff_dialog
        )
        add_btn.grid(row=0, column=1, padx=10, sticky="e")
    
    def create_staff_table(self):
        """Create scrollable staff table."""
        # Table container
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        # Headers
        headers = ["Name", "Title", "Contact", "Salary", "Join Date", 
                  "Last Paid", "Status", "Actions"]
        
        for col, text in enumerate(headers):
            ctk.CTkLabel(
                self.table_frame,
                text=text,
                font=FONTS["body"]
            ).grid(row=0, column=col, padx=10, pady=5, sticky="w")
        
        # Scrollable frame for staff list
        self.staff_frame = ctk.CTkScrollableFrame(self.table_frame)
        self.staff_frame.grid(row=1, column=0, columnspan=len(headers),
                            sticky="nsew", padx=5, pady=5)
    
    def create_payment_section(self):
        """Create payment history section."""
        self.payment_frame = ctk.CTkFrame(self)
        self.payment_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        # Title
        ctk.CTkLabel(
            self.payment_frame,
            text="Recent Payments",
            font=FONTS["subheading"]
        ).pack(pady=10)
    
    def load_staff_data(self):
        """Load staff data from database."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.id, s.name, s.title, s.contact, s.salary,
                       s.join_date, s.last_paid_date, s.is_active
                FROM staff s
                ORDER BY s.name
            """)
            
            self.staff_members = cursor.fetchall()
            self.update_staff_list()
            self.load_recent_payments()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load staff data: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def add_staff(self, name, title, contact, salary, join_date):
        """Add new staff member."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO staff (
                    name, title, contact, salary, join_date, is_active
                ) VALUES (?, ?, ?, ?, ?, 1)
            """, (name, title, contact, salary, join_date))
            
            conn.commit()
            messagebox.showinfo("Success", "Staff member added successfully")
            self.load_staff_data()  # Refresh list
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add staff: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def record_payment(self, staff_id, amount):
        """Record staff payment."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN")
            
            # Record payment
            cursor.execute("""
                INSERT INTO staff_payments (
                    staff_id, amount, payment_date
                ) VALUES (?, ?, DATE('now', 'localtime'))
            """, (staff_id, amount))
            
            # Update last paid date
            cursor.execute("""
                UPDATE staff
                SET last_paid_date = DATE('now', 'localtime')
                WHERE id = ?
            """, (staff_id,))
            
            # Add to expenses
            cursor.execute("""
                INSERT INTO expenses (
                    name, title, quantity, price_per_unit, total_price,
                    expense_date
                ) VALUES (
                    (SELECT name FROM staff WHERE id = ?),
                    'Salary Payment', 1, ?, ?,
                    DATE('now', 'localtime')
                )
            """, (staff_id, amount, amount))
            
            conn.commit()
            messagebox.showinfo("Success", "Payment recorded successfully")
            self.load_staff_data()  # Refresh list
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("Error", f"Failed to record payment: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def toggle_staff_status(self, staff_id, current_status):
        """Toggle staff active status."""
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
    
    def show_add_staff_dialog(self):
        """Show dialog for adding new staff member."""
        dialog = AddStaffDialog(self)
        dialog.focus()
    
    def show_payment_dialog(self, staff_id, staff_name, salary):
        """Show dialog for recording payment."""
        dialog = PaymentDialog(self, staff_id, staff_name, salary)
        dialog.focus()
    
    def update_staff_list(self):
        """Update staff list display."""
        # Clear current list
        for widget in self.staff_frame.winfo_children():
            widget.destroy()
        
        # Add staff members to list
        for row, staff in enumerate(self.staff_members):
            self.create_staff_row(row, staff)
    
    def create_staff_row(self, row, staff):
        """Create a row in the staff table."""
        # Unpack staff data
        staff_id, name, title, contact, salary, join_date, last_paid, is_active = staff
        
        # Create labels for each column
        cols = [name, title, contact, f"₹{salary:,.2f}", 
                join_date, last_paid or "Never", 
                "Active" if is_active else "Inactive"]
        
        for col, text in enumerate(cols):
            ctk.CTkLabel(
                self.staff_frame,
                text=str(text)
            ).grid(row=row, column=col, padx=10, pady=5, sticky="w")
        
        # Action buttons
        actions_frame = ctk.CTkFrame(self.staff_frame, fg_color="transparent")
        actions_frame.grid(row=row, column=len(cols), padx=10, pady=5)
        
        # Payment button
        if is_active:
            ctk.CTkButton(
                actions_frame,
                text="Pay",
                width=60,
                command=lambda: self.show_payment_dialog(staff_id, name, salary)
            ).pack(side="left", padx=5)
        
        # Toggle status button
        ctk.CTkButton(
            actions_frame,
            text="Deactivate" if is_active else "Activate",
            width=80,
            fg_color=COLORS["error"] if is_active else COLORS["success"],
            command=lambda: self.toggle_staff_status(staff_id, is_active)
        ).pack(side="left", padx=5)
    
    def load_recent_payments(self):
        """Load recent payment history."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.name, sp.amount, sp.payment_date
                FROM staff_payments sp
                JOIN staff s ON s.id = sp.staff_id
                ORDER BY sp.payment_date DESC
                LIMIT 5
            """)
            
            payments = cursor.fetchall()
            self.update_payment_history(payments)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load payment history: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def update_payment_history(self, payments):
        """Update payment history display."""
        # Clear current history
        for widget in self.payment_frame.winfo_children()[1:]:  # Keep the title
            widget.destroy()
        
        if not payments:
            ctk.CTkLabel(
                self.payment_frame,
                text="No recent payments",
                text_color=COLORS["text"]["secondary"]
            ).pack(pady=10)
        else:
            for payment in payments:
                name, amount, date = payment
                payment_frame = ctk.CTkFrame(self.payment_frame)
                payment_frame.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkLabel(
                    payment_frame,
                    text=name,
                    text_color=COLORS["text"]["primary"]
                ).pack(side="left", padx=5)
                
                ctk.CTkLabel(
                    payment_frame,
                    text=f"₹{amount:,.2f}",
                    text_color=COLORS["text"]["secondary"]
                ).pack(side="left", padx=5)
                
                ctk.CTkLabel(
                    payment_frame,
                    text=date,
                    text_color=COLORS["text"]["secondary"]
                ).pack(side="right", padx=5)
