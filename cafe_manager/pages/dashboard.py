"""
Dashboard page implementation for the Cafe Management System.
Provides analytics and insights through charts and statistics.
"""

import customtkinter as ctk
from utils.constants import *
from database import DatabaseManager
import sqlite3
from datetime import datetime, timedelta
import pytz  # Add timezone support
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

# Get local timezone
LOCAL_TZ = pytz.timezone('Asia/Kathmandu')  # Nepal Time (UTC+5:45)

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
    """Card showing popular items."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="white", corner_radius=10, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Popular Items",
            font=FONTS["default"],
            text_color=COLORS["text"]["secondary"]
        )
        self.title_label.grid(row=0, column=0, padx=PADDING["medium"], pady=(PADDING["medium"], 0), sticky="w")
        
        # Items container
        self.items_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.items_frame.grid(row=1, column=0, padx=PADDING["medium"], pady=(0, PADDING["medium"]), sticky="nsew")
        self.items_frame.grid_columnconfigure(0, weight=1)
    
    def update_items(self, items):
        """Update the displayed items."""
        # Clear existing items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        # Add new items
        for i, (name, count, quantity) in enumerate(items):
            item_text = f"{i+1}. {name} ({quantity} sold)"
            label = ctk.CTkLabel(
                self.items_frame,
                text=item_text,
                font=FONTS["small"],
                text_color=COLORS["text"]["primary"]
            )
            label.grid(row=i, column=0, pady=(0, 5), sticky="w")

class DashboardPage(ctk.CTkFrame):
    """Dashboard page showing analytics and insights."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=COLORS["background"])
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Store both sales and expense data
        self.sales_data = []
        self.expense_data = []
        self.current_period = "daily"
        
        # Initialize stat cards dictionary
        self.stat_cards = {}
        self.period_buttons = {}
        
        # Configure grid
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Setup UI components
        self.setup_ui()
        
        # Start auto-refresh
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Create and arrange all UI components."""
        self.create_chart_area()
        self.create_stats_area()
    
    def create_chart_area(self):
        """Create the chart area with period selection."""
        chart_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        chart_frame.grid(row=0, column=0, padx=PADDING["medium"], pady=PADDING["medium"], sticky="nsew")
        
        # Configure grid
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(1, weight=1)
        chart_frame.grid_rowconfigure(1, weight=1)
        
        # Period selection
        period_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
        period_frame.grid(row=0, column=0, columnspan=2, padx=PADDING["medium"], pady=PADDING["medium"], sticky="ew")
        
        periods = ["daily", "weekly", "monthly"]
        for i, period in enumerate(periods):
            btn = ctk.CTkButton(
                period_frame,
                text=period.capitalize(),
                fg_color="transparent" if period != "daily" else COLORS["primary"],
                text_color=COLORS["text"]["primary"] if period != "daily" else "white",
                command=lambda p=period: self.change_period(p)
            )
            btn.grid(row=0, column=i, padx=(0, PADDING["small"]))
            self.period_buttons[period] = btn
        
        # Create figures without pyplot - Make figures square and larger
        self.figure1 = matplotlib.figure.Figure(figsize=(8, 6))
        self.ax1 = self.figure1.add_subplot(111)
        
        self.figure2 = matplotlib.figure.Figure(figsize=(8, 6))
        self.ax2 = self.figure2.add_subplot(111)
        
        # Create canvases for both charts
        self.canvas1 = FigureCanvasTkAgg(self.figure1, master=chart_frame)
        self.canvas1.get_tk_widget().grid(row=1, column=0, padx=(PADDING["medium"], PADDING["small"]), pady=PADDING["medium"], sticky="nsew")
        
        self.canvas2 = FigureCanvasTkAgg(self.figure2, master=chart_frame)
        self.canvas2.get_tk_widget().grid(row=1, column=1, padx=(PADDING["small"], PADDING["medium"]), pady=PADDING["medium"], sticky="nsew")
    
    def setup_chart_style(self, ax):
        """Configure the matplotlib chart style for a given axis."""
        ax.set_facecolor(CHART_STYLE['background'])
        ax.figure.patch.set_facecolor(CHART_STYLE['background'])
        
        # Configure spines
        for spine in ax.spines.values():
            spine.set_color(CHART_STYLE['spine_color'])
        
        # Configure grid
        ax.grid(True, linestyle='--', alpha=CHART_STYLE['grid_alpha'], color=CHART_STYLE['grid_color'])
        
        # Configure ticks
        ax.tick_params(colors=CHART_STYLE['text_color'], grid_alpha=CHART_STYLE['grid_alpha'])
    
    def create_stats_area(self):
        """Create the statistics area."""
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=0, column=1, padx=PADDING["medium"], pady=PADDING["medium"], sticky="nsew")
        
        # Configure grid
        stats_frame.grid_columnconfigure(0, weight=1)
        
        # Create stat cards with proper titles
        self.stat_cards["Today's Revenue"] = StatCard(stats_frame, "Today's Revenue", "₹0.00")
        self.stat_cards["Today's Revenue"].grid(row=0, column=0, pady=(0, PADDING["medium"]), sticky="ew")
        
        self.stat_cards["Today's Expenses"] = StatCard(stats_frame, "Today's Expenses", "₹0.00")
        self.stat_cards["Today's Expenses"].grid(row=1, column=0, pady=(0, PADDING["medium"]), sticky="ew")
        
        self.stat_cards["Net Profit"] = StatCard(stats_frame, "Net Profit", "₹0.00")
        self.stat_cards["Net Profit"].grid(row=2, column=0, pady=(0, PADDING["medium"]), sticky="ew")
        
        # Create popular items card
        self.popular_items_card = PopularItemsCard(stats_frame)
        self.popular_items_card.grid(row=3, column=0, sticky="ew")
    
    def update_chart(self):
        """Update both charts with current data"""
        # Clear both charts
        self.ax1.clear()
        self.ax2.clear()
        self.setup_chart_style(self.ax1)
        self.setup_chart_style(self.ax2)
        
        # Update Revenue Chart (Line Chart)
        if self.sales_data:
            times = [row[0] for row in self.sales_data]
            sales = [float(row[1]) for row in self.sales_data]
            
            if self.current_period == "daily":
                times.reverse()
                sales.reverse()
            
            # Plot revenue line
            self.ax1.plot(times, sales, 
                         color='#3B82F6',  # Blue
                         label='Revenue',
                         linewidth=2,
                         marker='o',
                         markersize=6)
            
            # Customize revenue chart
            self.ax1.tick_params(colors=CHART_STYLE['text_color'], labelrotation=45)
            self.ax1.set_title('Revenue Overview',
                              pad=20, color=CHART_STYLE['title_color'], fontsize=12)
            self.ax1.set_xlabel('Time', color=CHART_STYLE['text_color'])
            self.ax1.set_ylabel('Amount (₹)', color=CHART_STYLE['text_color'])
            self.ax1.grid(True, linestyle='--', alpha=0.3)
            self.ax1.set_ylim(bottom=0)
            self.ax1.legend(loc='upper right')
        
        # Update Expense Chart (Pie Chart)
        if self.expense_data:
            # Prepare data for pie chart
            categories = [row[0] for row in self.expense_data]
            expenses = [float(row[1]) for row in self.expense_data]
            total_expenses = sum(expenses)
            
            # Modern color palette with vibrant colors
            colors = [
                '#FF6B6B',  # Coral Red
                '#4ECDC4',  # Turquoise
                '#45B7D1',  # Sky Blue
                '#96CEB4',  # Sage Green
                '#FFEEAD',  # Cream Yellow
                '#D4A5A5',  # Dusty Rose
                '#9A8194',  # Muted Purple
                '#392F5A',  # Deep Purple
                '#31A9B8',  # Teal
                '#FF9F1C',  # Orange
                '#2EC4B6',  # Mint
                '#E71D36',  # Bright Red
            ]
            
            # Remove the position setting to let it fill the available space
            # self.ax2.set_position([0.15, 0.1, 0.7, 0.7])  # Remove this line
            
            # Create pie chart with percentage labels
            wedges, texts, autotexts = self.ax2.pie(
                expenses,
                labels=categories,
                colors=colors,
                autopct=lambda pct: f'₹{int(pct*total_expenses/100):,}\n({pct:.1f}%)',
                pctdistance=0.85,  # Move percentage labels
                wedgeprops=dict(
                    width=0.5,  # Slightly thinner donut for better proportions
                    edgecolor='white',
                    linewidth=2,
                ),
                textprops={'fontsize': 10},  # Slightly larger text
                labeldistance=1.2,  # Move labels further out
            )
            
            # Customize pie chart text
            plt.setp(autotexts, size=9, weight="bold", color=CHART_STYLE['text_color'])
            plt.setp(texts, size=10, color=CHART_STYLE['text_color'])
            
            # Add title with padding
            period_text = {
                "daily": "Today's",
                "weekly": "This Week's",
                "monthly": "This Month's"
            }
            self.ax2.set_title(f"{period_text[self.current_period]} Expenses\nTotal: ₹{int(total_expenses):,}",
                              pad=20, color=CHART_STYLE['title_color'], fontsize=12, y=1.05)
            
            # Add center circle with gradient effect
            center_circle = plt.Circle((0,0), 0.70, fc='white')
            self.ax2.add_artist(center_circle)
            
            # Add subtle shadow effect
            shadow_circle = plt.Circle((0.02, -0.02), 0.70, fc='gray', alpha=0.2)
            self.ax2.add_artist(shadow_circle)
            
            # Equal aspect ratio ensures circular pie
            self.ax2.axis('equal')
        
        # Adjust layouts and draw
        self.figure1.tight_layout()
        self.figure2.tight_layout()
        self.canvas1.draw()
        self.canvas2.draw()
    
    def fetch_expenses_for_period(self, period="daily"):
        """Fetch expenses data for the specified period."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            now = datetime.now(LOCAL_TZ)
            today = now.strftime('%Y-%m-%d')
            
            if period == "daily":
                query = """
                    SELECT 
                        COALESCE(category, 'Other') as expense_category,
                        SUM(total_price) as total_expenses,
                        COUNT(*) as expense_count
                    FROM expenses
                    WHERE DATE(expense_date, '+5 hours', '45 minutes', 'localtime') = ?
                    GROUP BY category
                    ORDER BY total_expenses DESC
                """
                cursor.execute(query, (today,))
            elif period == "weekly":
                week_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
                query = """
                    SELECT 
                        COALESCE(category, 'Other') as expense_category,
                        SUM(total_price) as total_expenses,
                        COUNT(*) as expense_count
                    FROM expenses
                    WHERE DATE(expense_date, '+5 hours', '45 minutes', 'localtime') BETWEEN ? AND ?
                    GROUP BY category
                    ORDER BY total_expenses DESC
                """
                cursor.execute(query, (week_ago, today))
            else:  # monthly
                month_ago = (now - timedelta(days=30)).strftime('%Y-%m-%d')
                query = """
                    SELECT 
                        COALESCE(category, 'Other') as expense_category,
                        SUM(total_price) as total_expenses,
                        COUNT(*) as expense_count
                    FROM expenses
                    WHERE DATE(expense_date, '+5 hours', '45 minutes', 'localtime') BETWEEN ? AND ?
                    GROUP BY category
                    ORDER BY total_expenses DESC
                """
                cursor.execute(query, (month_ago, today))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Error fetching expenses data: {e}")
            return []
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def load_data(self):
        """Load all dashboard data."""
        try:
            # Fetch both sales and expense data
            self.sales_data = self.fetch_sales_data(self.current_period)
            self.expense_data = self.fetch_expenses_for_period(self.current_period)
            self.update_chart()
            self.update_stats()
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def fetch_sales_data(self, period="daily"):
        """Fetch sales data for the specified period."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Get current time in local timezone
            now = datetime.now(LOCAL_TZ)
            today = now.strftime('%Y-%m-%d')
            
            if period == "daily":
                query = """
                    SELECT 
                        strftime('%I:%M %p', datetime(created_at, '+5 hours', '45 minutes', 'localtime')) as time_period,
                        SUM(total_amount) as total_sales,
                        COUNT(*) as transaction_count
                    FROM sales
                    WHERE DATE(created_at, '+5 hours', '45 minutes', 'localtime') = ?
                    GROUP BY strftime('%H:%M', datetime(created_at, '+5 hours', '45 minutes', 'localtime'))
                    ORDER BY strftime('%H:%M', datetime(created_at, '+5 hours', '45 minutes', 'localtime')) DESC
                    LIMIT 30
                """
                cursor.execute(query, (today,))
            elif period == "weekly":
                week_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
                query = """
                    SELECT 
                        DATE(created_at, '+5 hours', '45 minutes', 'localtime') as date,
                        SUM(total_amount) as total_sales,
                        COUNT(*) as transaction_count
                    FROM sales
                    WHERE DATE(created_at, '+5 hours', '45 minutes', 'localtime') BETWEEN ? AND ?
                    GROUP BY DATE(created_at, '+5 hours', '45 minutes', 'localtime')
                    ORDER BY date
                """
                cursor.execute(query, (week_ago, today))
            else:  # monthly
                month_ago = (now - timedelta(days=30)).strftime('%Y-%m-%d')
                query = """
                    SELECT 
                        strftime('%Y-%m-%d', datetime(created_at, '+5 hours', '45 minutes', 'localtime')) as month,
                        SUM(total_amount) as total_sales,
                        COUNT(*) as transaction_count
                    FROM sales
                    WHERE DATE(created_at, '+5 hours', '45 minutes', 'localtime') BETWEEN ? AND ?
                    GROUP BY strftime('%Y-%m-%d', datetime(created_at, '+5 hours', '45 minutes', 'localtime'))
                    ORDER BY month
                """
                cursor.execute(query, (month_ago, today))
            
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
            
            # Get current time in local timezone
            now = datetime.now(LOCAL_TZ)
            today = now.strftime('%Y-%m-%d')
            week_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
            month_ago = (now - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Get period-specific labels
            period_labels = {
                "daily": "Today's",
                "weekly": "This Week's",
                "monthly": "This Month's"
            }
            
            # Fetch sales based on period
            if self.current_period == "daily":
                sales_query = """
                    SELECT COALESCE(SUM(total_amount), 0)
                    FROM sales
                    WHERE DATE(created_at, '+5 hours', '45 minutes', 'localtime') = ?
                """
                cursor.execute(sales_query, (today,))
            elif self.current_period == "weekly":
                sales_query = """
                    SELECT COALESCE(SUM(total_amount), 0)
                    FROM sales
                    WHERE DATE(created_at, '+5 hours', '45 minutes', 'localtime') BETWEEN ? AND ?
                """
                cursor.execute(sales_query, (week_ago, today))
            else:  # monthly
                sales_query = """
                    SELECT COALESCE(SUM(total_amount), 0)
                    FROM sales
                    WHERE DATE(created_at, '+5 hours', '45 minutes', 'localtime') BETWEEN ? AND ?
                """
                cursor.execute(sales_query, (month_ago, today))
            
            period_sales = cursor.fetchone()[0]
            
            # Fetch expenses based on period
            if self.current_period == "daily":
                expenses_query = """
                    SELECT COALESCE(SUM(total_price), 0)
                    FROM expenses
                    WHERE DATE(expense_date, '+5 hours', '45 minutes', 'localtime') = ?
                """
                cursor.execute(expenses_query, (today,))
            elif self.current_period == "weekly":
                expenses_query = """
                    SELECT COALESCE(SUM(total_price), 0)
                    FROM expenses
                    WHERE DATE(expense_date, '+5 hours', '45 minutes', 'localtime') BETWEEN ? AND ?
                """
                cursor.execute(expenses_query, (week_ago, today))
            else:  # monthly
                expenses_query = """
                    SELECT COALESCE(SUM(total_price), 0)
                    FROM expenses
                    WHERE DATE(expense_date, '+5 hours', '45 minutes', 'localtime') BETWEEN ? AND ?
                """
                cursor.execute(expenses_query, (month_ago, today))
            
            period_expenses = cursor.fetchone()[0]
            
            # Update stat cards with period-specific titles
            self.stat_cards["Today's Revenue"].title_label.configure(
                text=f"{period_labels[self.current_period]} Revenue"
            )
            self.stat_cards["Today's Revenue"].update_value(f"₹{period_sales:,.2f}")
            
            self.stat_cards["Today's Expenses"].title_label.configure(
                text=f"{period_labels[self.current_period]} Expenses"
            )
            self.stat_cards["Today's Expenses"].update_value(f"₹{period_expenses:,.2f}")
            
            self.stat_cards["Net Profit"].title_label.configure(
                text=f"{period_labels[self.current_period]} Net Profit"
            )
            self.stat_cards["Net Profit"].update_value(f"₹{period_sales - period_expenses:,.2f}")
            
            # Fetch popular items based on period
            if self.current_period == "daily":
                popular_query = """
                    SELECT 
                        m.name,
                        COUNT(*) as order_count,
                        SUM(si.quantity) as total_quantity
                    FROM sale_items si
                    JOIN menu_items m ON m.id = si.menu_item_id
                    JOIN sales s ON s.id = si.sale_id
                    WHERE DATE(s.created_at, '+5 hours', '45 minutes', 'localtime') = ?
                    GROUP BY m.id
                    ORDER BY order_count DESC
                    LIMIT 5
                """
                cursor.execute(popular_query, (today,))
            elif self.current_period == "weekly":
                popular_query = """
                    SELECT 
                        m.name,
                        COUNT(*) as order_count,
                        SUM(si.quantity) as total_quantity
                    FROM sale_items si
                    JOIN menu_items m ON m.id = si.menu_item_id
                    JOIN sales s ON s.id = si.sale_id
                    WHERE DATE(s.created_at, '+5 hours', '45 minutes', 'localtime') BETWEEN ? AND ?
                    GROUP BY m.id
                    ORDER BY order_count DESC
                    LIMIT 5
                """
                cursor.execute(popular_query, (week_ago, today))
            else:  # monthly
                popular_query = """
                    SELECT 
                        m.name,
                        COUNT(*) as order_count,
                        SUM(si.quantity) as total_quantity
                    FROM sale_items si
                    JOIN menu_items m ON m.id = si.menu_item_id
                    JOIN sales s ON s.id = si.sale_id
                    WHERE DATE(s.created_at, '+5 hours', '45 minutes', 'localtime') BETWEEN ? AND ?
                    GROUP BY m.id
                    ORDER BY order_count DESC
                    LIMIT 5
                """
                cursor.execute(popular_query, (month_ago, today))
            
            popular_items = cursor.fetchall()
            self.popular_items_card.title_label.configure(
                text=f"{period_labels[self.current_period]} Popular Items"
            )
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
        self.after(1000, self.start_auto_refresh)  # Refresh every second
    
    def destroy(self):
        """Clean up resources."""
        plt.close(self.figure1)
        plt.close(self.figure2)
        super().destroy()
