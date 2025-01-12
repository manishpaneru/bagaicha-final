"""
Login window implementation for the Cafe Management System.
Handles user authentication and provides access to the main application.
"""

import customtkinter as ctk
from utils.constants import WINDOW_CONFIG, COLORS, FONTS, PADDING, ERROR_MESSAGES
from database import DatabaseManager
import sqlite3
from tkinter import messagebox

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title(WINDOW_CONFIG["login"]["title"])
        self.geometry(f"{WINDOW_CONFIG['login']['width']}x{WINDOW_CONFIG['login']['height']}")
        self.resizable(False, False)
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Initialize UI
        self.setup_ui()
        self.center_window()

    def center_window(self):
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - WINDOW_CONFIG["login"]["width"]) // 2
        y = (screen_height - WINDOW_CONFIG["login"]["height"]) // 2
        
        # Set position
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main frame
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.main_frame.grid(row=0, column=0, padx=PADDING["large"], pady=PADDING["large"], sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Title Label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Café Manager",
            font=FONTS["heading"]
        )
        self.title_label.grid(row=0, column=0, pady=(0, PADDING["large"]))

        # Username Entry
        self.username_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Username",
            width=250,
            height=40
        )
        self.username_entry.grid(row=1, column=0, pady=PADDING["medium"])

        # Password Entry
        self.password_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Password",
            show="●",
            width=250,
            height=40
        )
        self.password_entry.grid(row=2, column=0, pady=PADDING["medium"])

        # Login Button
        self.login_button = ctk.CTkButton(
            self.main_frame,
            text="Login",
            width=200,
            height=40,
            command=self.login
        )
        self.login_button.grid(row=3, column=0, pady=PADDING["large"])

        # Error Label
        self.error_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            text_color=COLORS["error"],
            font=FONTS["small"]
        )
        self.error_label.grid(row=4, column=0, pady=PADDING["small"])

        # Bind enter key
        self.bind("<Return>", lambda event: self.login())
        
        # Set initial focus
        self.username_entry.focus()

        # Bind key events to clear error
        self.username_entry.bind("<Key>", lambda event: self.clear_error())
        self.password_entry.bind("<Key>", lambda event: self.clear_error())

    def login(self):
        # Clear previous error
        self.error_label.configure(text="")
        
        # Get credentials
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Validate empty fields
        if not username or not password:
            self.error_label.configure(text=ERROR_MESSAGES["login"]["empty_fields"])
            return
        
        # Verify credentials
        if username == "admin" and password == "pass":
            self.success_login()
        else:
            self.error_label.configure(text=ERROR_MESSAGES["login"]["invalid_credentials"])
            self.password_entry.delete(0, 'end')
            self.username_entry.focus()

    def success_login(self):
        self.withdraw()  # Hide login window
        try:
            from main import CafeManager
            main_window = CafeManager(self)
            main_window.mainloop()
        except Exception as e:
            messagebox.showerror("Error", "Failed to load main window")
            self.deiconify()  # Show login window again

    def clear_error(self):
        """Clear error message when user starts typing"""
        self.error_label.configure(text="")

if __name__ == "__main__":
    # Set theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create login window
    app = LoginWindow()
    app.mainloop() 