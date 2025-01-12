"""
Configuration constants for the Cafe Management System.
Contains all the static configurations used throughout the application.
"""

import os

# Window Configurations
WINDOW_CONFIG = {
    "login": {
        "width": 400,
        "height": 500,
        "title": "Café Manager - Login"
    },
    "main": {
        "width": 1200,
        "height": 800,
        "min_width": 800,
        "min_height": 600,
        "title": "Café Manager"
    }
}

# Layout Constants
PADDING = {
    "small": 5,
    "medium": 10,
    "large": 20,
    "xlarge": 30
}

# Font Configurations
FONTS = {
    "heading": ("Helvetica", 24, "bold"),
    "subheading": ("Helvetica", 18, "bold"),
    "body": ("Helvetica", 14),
    "default": ("Helvetica", 12),
    "small": ("Helvetica", 10)
}

# Color Schemes
COLORS = {
    "primary": "#1f538d",
    "secondary": "#14375e",
    "accent": "#ff9800",
    "success": "#2ecc71",
    "warning": "#f1c40f",
    "error": "#e74c3c",
    "background": "#2b2b2b",
    "surface": "#333333",
    "text": {
        "primary": "#000000",
        "secondary": "#666666",
        "disabled": "#999999"
    }
}

# Page Configurations
PAGES = {
    "dashboard": {"name": "Dashboard", "icon": "dashboard.png"},
    "sales": {"name": "Sales", "icon": "sales.png"},
    "expenses": {"name": "Expenses", "icon": "expenses.png"},
    "bar_stock": {"name": "Bar Stock", "icon": "stock.png"},
    "staff": {"name": "Staff", "icon": "staff.png"},
    "menu": {"name": "Menu", "icon": "menu.png"}
}

# Database Configuration
DB_CONFIG = {
    "filename": "cafe_manager.db",
    "timeout": 30,
    "check_same_thread": False
}

# Error Messages
ERROR_MESSAGES = {
    "login": {
        "invalid_credentials": "Invalid username or password",
        "connection_failed": "Database connection failed",
        "empty_fields": "Please fill all fields"
    },
    "main": {
        "load_failed": "Failed to load page",
        "db_error": "Database error occurred",
        "session_expired": "Session expired, please login again"
    }
}

# Success Messages
SUCCESS_MESSAGES = {
    "login": "Login successful",
    "logout": "Logout successful",
    "save": "Changes saved successfully"
}

# Application Paths
APP_PATHS = {
    "root": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"),
    "logs": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
}

# Notification Settings
NOTIFICATION_CONFIG = {
    "check_interval": 300000,  # 5 minutes in milliseconds
    "display_time": 5000,      # 5 seconds in milliseconds
    "stock_threshold": 10      # Minimum stock level for notifications
}

# Input Validation
VALIDATION = {
    "username": {
        "min_length": 3,
        "max_length": 50
    },
    "password": {
        "min_length": 6,
        "max_length": 50
    }
}

# Layout Dimensions
SIDEBAR_WIDTH = 250
HEADER_HEIGHT = 60
NOTIFICATION_CHECK_INTERVAL = 300000  # 5 minutes in milliseconds

# Animation Settings
ANIMATION = {
    "duration": 300,  # milliseconds
    "transition": "ease_out"
} 