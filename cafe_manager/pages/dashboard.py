"""
Dashboard page implementation for the Cafe Management System.
Provides analytics and insights through charts and statistics.
"""

import customtkinter as ctk
from utils.constants import *
from database import DatabaseManager
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')  # Must be before any other matplotlib imports

# Chart style configuration
CHART_STYLE = {
    'background': 'white',
    'grid_color': '#E5E7EB',
    'grid_alpha': 0.3,
    'line_color': '#3B82F6',
    'text_color': '#4B5563',
    'title_color': '#1F2937',
    'spine_color': '#E5E7EB'
}

class StatCard(ctk.CTkFrame):
    """Custom widget for displaying statistics."""
    
    def __init__(self, parent, title, value="0", **kwargs):
        super().__init__(parent, fg_color="white", corner_radius=10, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=FONTS["default"],
            text_color=COLORS["text"]["secondary"]
        )
        self.title_label.grid(row=0, column=0, padx=PADDING["medium"], pady=(PADDING["medium"], 0), sticky="w")
        
        # Value
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=FONTS["subheading"],
            text_color=COLORS["text"]["primary"]
        )
        self.value_label.grid(row=1, column=0, padx=PADDING["medium"], pady=(0, PADDING["medium"]), sticky="w")
    
    def update_value(self, value):
        """Update the displayed value."""
        self.value_label.configure(text=value)

class PopularItemsCard(ctk.CTkFrame):
    """Custom widget for displaying popular items."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="white", corner_radius=10, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        ctk.CTkLabel(
            self,
            text="Popular Items Today",
            font=FONTS["default"],
            text_color=COLORS["text"]["secondary"]
        ).grid(row=0, column=0, padx=PADDING["medium"], pady=PADDING["medium"], sticky="w")
        
        # Items container
        self.items_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.items_frame.grid(row=1, column=0, sticky="nsew", padx=PADDING["medium"], pady=(0, PADDING["medium"]))
        
        # Create item labels
        self.item_labels = []
        for i in range(5):
            label = ctk.CTkLabel(
                self.items_frame,
                text="",
                font=FONTS["default"],
                text_color=COLORS["text"]["primary"]
            )
            label.pack(anchor="w", pady=2)
            self.item_labels.append(label)
    
    def update_items(self, items):
        """Update the displayed items."""
        for i, label in enumerate(self.item_labels):
            if i < len(items):
                item = items[i]
                label.configure(text=f"{i+1}. {item[0]} ({item[2]} sold)")
            else:
                label.configure(text="")

class DashboardPage(ctk.CTkFrame):
    """Dashboard page showing analytics and insights."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Initialize variables
        self.db = DatabaseManager()
        self.current_period = "daily"
        self.chart_data = None
        self.stats_data = None
        self.stat_cards = {}
        
        # Configure grid
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_data()
        
        # Set up auto-refresh
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Create and arrange all UI components."""
        self.create_chart_area()
        self.create_stats_area()
    
    def create_chart_area(self):
        """Create the chart area with period selector and graph."""
        # Chart container
        self.chart_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=10
        )
        self.chart_frame.grid(
            row=0, column=0,
            padx=(PADDING["medium"], PADDING["small"]),
            pady=PADDING["medium"],
            sticky="nsew"
        )
        
        # Period selector
        self.period_frame = ctk.CTkFrame(
            self.chart_frame,
            fg_color="transparent"
        )
        self.period_frame.pack(fill="x", padx=PADDING["medium"], pady=PADDING["medium"])
        
        self.period_buttons = {}
        for period in ["Daily", "Weekly", "Monthly"]:
            btn = ctk.CTkButton(
                self.period_frame,
                text=period,
                width=100,
                fg_color=COLORS["primary"] if period.lower() == self.current_period else "transparent",
                text_color="white" if period.lower() == self.current_period else COLORS["text"]["primary"],
                command=lambda p=period.lower(): self.change_period(p)
            )
            btn.pack(side="left", padx=5)
            self.period_buttons[period.lower()] = btn
        
        # Chart area
        self.figure, self.ax = plt.subplots(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=PADDING["medium"], pady=(0, PADDING["medium"]))
        
        # Configure chart style
        self.setup_chart_style()
    
    def setup_chart_style(self):
        """Configure the matplotlib chart style."""
        self.ax.set_facecolor(CHART_STYLE['background'])
        self.figure.patch.set_facecolor(CHART_STYLE['background'])
        
        # Configure spines
        for spine in self.ax.spines.values():
            spine.set_color(CHART_STYLE['spine_color'])
        
        # Configure grid
        self.ax.grid(True, linestyle='--', alpha=CHART_STYLE['grid_alpha'], color=CHART_STYLE['grid_color'])
        
        # Configure ticks
        self.ax.tick_params(colors=CHART_STYLE['text_color'], grid_alpha=CHART_STYLE['grid_alpha'])
    
    def create_stats_area(self):
        """Create the statistics area with cards."""
        # Stats container
        self.stats_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.stats_frame.grid(
            row=0, column=1,
            padx=(PADDING["small"], PADDING["medium"]),
            pady=PADDING["medium"],
            sticky="nsew"
        )
        
        # Configure grid
        self.stats_frame.grid_columnconfigure(0, weight=1)
        
        # Create stat cards
        stats = [
            ("Today's Revenue", "₹0"),
            ("Today's Expenses", "₹0"),
            ("Net Profit", "₹0")
        ]
        
        for i, (title, value) in enumerate(stats):
            card = StatCard(self.stats_frame, title, value)
            card.grid(row=i, column=0, sticky="ew", pady=(0, PADDING["medium"]))
            self.stat_cards[title] = card
        
        # Popular items card
        self.popular_items_card = PopularItemsCard(self.stats_frame)
        self.popular_items_card.grid(row=len(stats), column=0, sticky="ew")
    
    def update_chart(self):
        """Update chart with current data"""
        self.ax.clear()
        self.setup_chart_style()
        
        # Get data
        sales_data = self.chart_data
        
        if not sales_data:
            self.ax.text(0.5, 0.5, 'No data available', 
                        horizontalalignment='center',
                        verticalalignment='center',
                        color=CHART_STYLE['text_color'])
        else:
            # Prepare data
            dates = [row[0] for row in sales_data]
            sales = [row[1] for row in sales_data]
            
            # Plot with matplotlib styling
            self.ax.plot(dates, sales, 
                        marker='o',
                        color=CHART_STYLE['line_color'],
                        linewidth=2,
                        markersize=6)
            
            # Customize ticks
            self.ax.tick_params(colors=CHART_STYLE['text_color'], grid_alpha=CHART_STYLE['grid_alpha'])
            
            # Rotate labels if needed
            plt.xticks(rotation=45 if self.current_period != "daily" else 0)
            
            # Title and labels
            self.ax.set_title(f'{self.current_period.capitalize()} Sales Overview',
                            pad=20, color=CHART_STYLE['title_color'], fontsize=12)
            self.ax.set_ylabel('Sales (₹)', color=CHART_STYLE['text_color'])
            
        # Adjust layout
        self.figure.tight_layout()
        self.canvas.draw()
    
    def load_data(self):
        """Load all dashboard data."""
        try:
            # Show loading state
            self.chart_data = self.fetch_sales_data(self.current_period)
            self.update_chart()
            self.update_stats()
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def fetch_sales_data(self, period="daily"):
        """Fetch sales data for the specified period."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            if period == "daily":
                query = """
                    SELECT 
                        strftime('%H:00', created_at) as time_period,
                        SUM(total_amount) as total_sales,
                        COUNT(*) as transaction_count
                    FROM sales
                    WHERE DATE(created_at) = DATE('now', 'localtime')
                    GROUP BY strftime('%H', created_at)
                    ORDER BY time_period
                """
            elif period == "weekly":
                query = """
                    SELECT 
                        DATE(created_at) as date,
                        SUM(total_amount) as total_sales,
                        COUNT(*) as transaction_count
                    FROM sales
                    WHERE created_at >= DATE('now', '-7 days')
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """
            else:  # monthly
                query = """
                    SELECT 
                        strftime('%Y-%m', created_at) as month,
                        SUM(total_amount) as total_sales,
                        COUNT(*) as transaction_count
                    FROM sales
                    WHERE created_at >= DATE('now', '-30 days')
                    GROUP BY strftime('%Y-%m', created_at)
                    ORDER BY month
                """
            
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Error fetching sales data: {e}")
            return []
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def fetch_popular_items(self):
        """Fetch top selling items for today."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    m.name,
                    COUNT(*) as order_count,
                    SUM(si.quantity) as total_quantity
                FROM sale_items si
                JOIN menu_items m ON si.menu_item_id = m.id
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.created_at) = DATE('now', 'localtime')
                GROUP BY m.id
                ORDER BY order_count DESC
                LIMIT 5
            """
            
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Error fetching popular items: {e}")
            return []
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def update_stats(self):
        """Update all statistics."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Today's total sales
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0)
                FROM sales
                WHERE DATE(created_at) = DATE('now', 'localtime')
            """)
            today_sales = cursor.fetchone()[0]
            
            # Today's expenses
            cursor.execute("""
                SELECT COALESCE(SUM(total_price), 0)
                FROM expenses
                WHERE DATE(expense_date) = DATE('now', 'localtime')
            """)
            today_expenses = cursor.fetchone()[0]
            
            # Update stat cards
            self.stat_cards["Today's Revenue"].update_value(f"₹{today_sales:,.2f}")
            self.stat_cards["Today's Expenses"].update_value(f"₹{today_expenses:,.2f}")
            self.stat_cards["Net Profit"].update_value(f"₹{today_sales - today_expenses:,.2f}")
            
            # Update popular items
            popular_items = self.fetch_popular_items()
            self.popular_items_card.update_items(popular_items)
            
        except Exception as e:
            print(f"Error updating stats: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def change_period(self, period):
        """Change the chart period."""
        self.current_period = period
        
        # Update button states
        for p, btn in self.period_buttons.items():
            btn.configure(
                fg_color=COLORS["primary"] if p == period else "transparent",
                text_color="white" if p == period else COLORS["text"]["primary"]
            )
        
        # Reload data
        self.load_data()
    
    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        self.load_data()
        self.after(300000, self.start_auto_refresh)  # Refresh every 5 minutes
    
    def destroy(self):
        """Clean up resources."""
        plt.close(self.figure)
        super().destroy()
