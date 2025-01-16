"""
Main application window for the Cafe Management System.
Handles the core UI and navigation between different pages.
"""

import customtkinter as ctk
from utils.constants import *
from database import DatabaseManager
from datetime import datetime
import sqlite3
from tkinter import messagebox
import threading
from PIL import Image
import time
import sys
import os

# Import pages
from pages.dashboard import DashboardPage
from pages.analytics import AnalyticsPage
from pages.sales import SalesPage
from pages.expenses import ExpensesPage
from pages.bar_stock import BarStockPage
from pages.staff import StaffPage
from pages.menu import MenuPage

class NotificationManager:
    """Handles system notifications and alerts."""
    
    def __init__(self, parent):
        """Initialize notification manager.
        
        Args:
            parent: Parent window reference
        """
        self.parent = parent
        self.notifications = []
        self.last_check = None
        
    def check_notifications(self):
        """Check for system notifications (low stock, etc.)."""
        try:
            db = DatabaseManager()
            conn = db.connect()
            cursor = conn.cursor()
            
            # Check bar stock
            cursor.execute("""
                SELECT item_name, quantity, min_threshold 
                FROM bar_stock 
                WHERE quantity <= min_threshold
            """)
            low_stock = cursor.fetchall()
            
            # Update notifications
            self.notifications = [
                f"Low Stock: {item[0]} ({item[1]} remaining)"
                for item in low_stock
            ]
            
            # Update notification icon
            self.parent.update_notification_icon(bool(self.notifications))
            
        except Exception as e:
            print(f"Notification check failed: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
            
        # Schedule next check
        self.parent.after(NOTIFICATION_CHECK_INTERVAL, self.check_notifications)

class CafeManager(ctk.CTk):
    """Main application window for the Cafe Management System."""
    
    def __init__(self, login_window=None):
        """Initialize the main window.
        
        Args:
            login_window: Reference to the login window
        """
        super().__init__()
        
        # Initialize variables
        self.login_window = login_window
        self.current_page = None
        self.nav_buttons = {}
        self.pages = {}
        self.db = DatabaseManager()
        
        # Initialize managers
        self.notification_manager = NotificationManager(self)
        
        # Window setup
        self.title(WINDOW_CONFIG["main"]["title"])
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Set window size to full screen width and 90% of screen height
        window_height = int(screen_height * 0.9)
        self.geometry(f"{screen_width}x{window_height}+0+0")
        
        # Set minimum size
        self.minsize(screen_width, 600)
        
        # Ensure window is maximized horizontally
        self.resizable(False, True)  # Allow only vertical resizing
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Event bindings
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Control-q>", lambda e: self.on_closing())
        self.bind("<Control-l>", lambda e: self.logout())
        
        # Setup UI
        self.setup_ui()
        
        # Start background tasks
        self.start_background_tasks()

    def setup_ui(self):
        """Create and arrange all UI components."""
        # Create main sections
        self.create_sidebar()
        self.create_header()
        self.create_main_frame()
        
        # Switch to default page
        self.switch_page("dashboard")

    def create_sidebar(self):
        """Create the sidebar with navigation buttons."""
        # Sidebar container
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color="white",
            width=SIDEBAR_WIDTH,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # App title
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(fill="x", padx=PADDING["medium"], pady=PADDING["medium"])
        
        ctk.CTkLabel(
            title_frame,
            text="Café Manager",
            font=FONTS["heading"],
            text_color=COLORS["text"]["primary"]
        ).pack(pady=PADDING["medium"])
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", expand=True, pady=PADDING["medium"])
        
        for page_id, page_info in PAGES.items():
            btn = self.create_nav_button(
                nav_frame,
                text=page_info["name"],
                command=lambda p=page_id: self.switch_page(p)
            )
            btn.pack(fill="x", padx=PADDING["medium"], pady=2)
            self.nav_buttons[page_id] = btn
        
        # Logout button at bottom
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color=COLORS["error"],
            hover_color="#D32F2F",
            command=self.logout
        )
        logout_btn.pack(pady=PADDING["large"], padx=PADDING["medium"], side="bottom")

    def create_header(self):
        """Create the header with title and notifications."""
        self.header = ctk.CTkFrame(
            self,
            fg_color="white",
            height=HEADER_HEIGHT,
            corner_radius=0
        )
        self.header.grid(row=0, column=1, sticky="ew")
        self.header.grid_propagate(False)
        
        # Configure header grid
        self.header.grid_columnconfigure(0, weight=1)
        
        # Page title
        self.page_title = ctk.CTkLabel(
            self.header,
            text="Dashboard",
            font=FONTS["subheading"],
            text_color=COLORS["text"]["primary"]
        )
        self.page_title.grid(row=0, column=0, padx=PADDING["large"], pady=PADDING["medium"], sticky="w")
        
        # Notification button
        self.notification_btn = ctk.CTkButton(
            self.header,
            text="🔔",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color=COLORS["background"],
            command=self.show_notifications
        )
        self.notification_btn.grid(row=0, column=1, padx=PADDING["medium"])

    def create_main_frame(self):
        """Create the main content area."""
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["background"],
            corner_radius=0
        )
        self.main_frame.grid(row=1, column=1, sticky="nsew")
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def create_nav_button(self, master, text, command):
        """Create a navigation button with consistent styling.
        
        Args:
            master: Parent widget
            text: Button text
            command: Button command
            
        Returns:
            CTkButton: The created button
        """
        return ctk.CTkButton(
            master=master,
            text=text,
            fg_color="transparent",
            text_color=COLORS["text"]["secondary"],
            hover_color=COLORS["background"],
            anchor="w",
            height=45,
            command=command
        )

    def switch_page(self, page_id):
        """Switch to the specified page."""
        try:
            # Clear current page
            if self.current_page:
                self.current_page.destroy()
            
            # Update navigation buttons
            for btn_id, btn in self.nav_buttons.items():
                if btn_id == page_id:
                    btn.configure(fg_color=COLORS["primary"])
                else:
                    btn.configure(fg_color="transparent")
            
            # Update page title
            self.page_title.configure(text=PAGES[page_id]["name"])
            
            # Create new page
            if page_id == "dashboard":
                self.current_page = DashboardPage(self.main_frame)
            elif page_id == "analytics":
                self.current_page = AnalyticsPage(self.main_frame)
            elif page_id == "sales":
                self.current_page = SalesPage(self.main_frame)
            elif page_id == "expenses":
                self.current_page = ExpensesPage(self.main_frame)
            elif page_id == "bar_stock":
                self.current_page = BarStockPage(self.main_frame)
            elif page_id == "staff":
                self.current_page = StaffPage(self.main_frame)
            elif page_id == "menu":
                self.current_page = MenuPage(self.main_frame)
            
            # Display new page
            self.current_page.grid(row=0, column=0, sticky="nsew")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load page: {str(e)}")

    def show_notifications(self):
        """Display current notifications."""
        if self.notification_manager.notifications:
            messagebox.showinfo(
                "Notifications",
                "\n".join(self.notification_manager.notifications)
            )
        else:
            messagebox.showinfo("Notifications", "No notifications")

    def update_notification_icon(self, has_notifications):
        """Update the notification icon state.
        
        Args:
            has_notifications: Whether there are active notifications
        """
        self.notification_btn.configure(
            fg_color=COLORS["warning"] if has_notifications else "transparent",
            text="🔔" if has_notifications else "🔕"
        )

    def start_background_tasks(self):
        """Start background tasks like notification checking."""
        # Start notification checker
        self.notification_manager.check_notifications()

    def logout(self):
        """Handle user logout."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Clean up resources
            if self.db.conn:
                self.db.close()
            
            # Show login window if exists
            if self.login_window:
                self.login_window.deiconify()
                self.login_window.username_entry.delete(0, 'end')
                self.login_window.password_entry.delete(0, 'end')
                self.login_window.username_entry.focus()
            
            # Close main window
            self.destroy()

    def on_closing(self):
        """Handle window closing."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            # Clean up resources
            if self.db.conn:
                self.db.close()
            
            # Close application
            self.destroy()
            sys.exit()

    def center_window(self):
        """Center the window on the screen."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_CONFIG["main"]["width"]) // 2
        y = (screen_height - WINDOW_CONFIG["main"]["height"]) // 2
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    # Set theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run application
    app = CafeManager()
    app.mainloop()
