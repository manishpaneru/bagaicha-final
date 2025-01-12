import os
import sys
import customtkinter as ctk
from PIL import Image
from tkcalendar import DateEntry
import sqlite3

from cafe_manager.pages.staff import StaffPage
from cafe_manager.pages.sales import SalesPage
from cafe_manager.pages.expenses import ExpensesPage
from cafe_manager.pages.bar_stock import BarStockPage
from cafe_manager.utils.constants import FONTS, WINDOW_CONFIG

class CafeManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set window title
        self.title("Tropical Bagaicha - Restaurant & Bar")

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        window_height = int(self.winfo_screenheight() * 0.9)  # 90% of screen height

        # Set window size and position
        self.geometry(f"{screen_width}x{window_height}+0+0")
        self.minsize(screen_width, 600)
        self.resizable(False, True)  # Allow only vertical resizing

        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True)

        # Initialize pages
        self.current_page = None
        self.show_page("staff")

    def show_page(self, page_name):
        # Destroy current page if exists
        if self.current_page:
            self.current_page.destroy()

        # Create new page
        if page_name == "staff":
            self.current_page = StaffPage(self.main_container)
        elif page_name == "sales":
            self.current_page = SalesPage(self.main_container)
        elif page_name == "expenses":
            self.current_page = ExpensesPage(self.main_container)
        elif page_name == "bar_stock":
            self.current_page = BarStockPage(self.main_container)

        self.current_page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = CafeManager()
    app.mainloop() 