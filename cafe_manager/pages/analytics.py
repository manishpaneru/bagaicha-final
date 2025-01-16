"""
Analytics page implementation for the Cafe Management System.
Provides detailed business insights and trends through interactive visualizations.
"""

import customtkinter as ctk
from utils.constants import *
from database import DatabaseManager
import sqlite3
from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

# Get local timezone
LOCAL_TZ = pytz.timezone('Asia/Kathmandu')  # Nepal Time (UTC+5:45)

class InsightCard(ctk.CTkFrame):
    """Custom widget for displaying business insights."""
    
    def __init__(self, parent, title, value="", subtitle="", **kwargs):
        super().__init__(parent, fg_color="white", corner_radius=10, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=FONTS["small"],
            text_color=COLORS["text"]["secondary"]
        )
        self.title_label.grid(row=0, column=0, padx=PADDING["medium"], pady=(PADDING["medium"], 0), sticky="w")
        
        # Value
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=FONTS["heading"],
            text_color=COLORS["text"]["primary"]
        )
        self.value_label.grid(row=1, column=0, padx=PADDING["medium"], pady=(0, PADDING["small"]), sticky="w")
        
        # Subtitle
        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=FONTS["small"],
                text_color=COLORS["text"]["secondary"]
            )
            self.subtitle_label.grid(row=2, column=0, padx=PADDING["medium"], pady=(0, PADDING["medium"]), sticky="w")
    
    def update(self, value, subtitle=""):
        """Update the displayed value and subtitle."""
        self.value_label.configure(text=value)
        if hasattr(self, 'subtitle_label') and subtitle:
            self.subtitle_label.configure(text=subtitle)

class AnalyticsPage(ctk.CTkFrame):
    """Analytics page showing detailed business insights."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=COLORS["background"])
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Setup UI components
        self.setup_ui()
        
        # Start auto-refresh
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Create and arrange all UI components."""
        # Title Section
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=PADDING["medium"], pady=PADDING["medium"], sticky="ew")
        
        ctk.CTkLabel(
            title_frame,
            text="Business Analytics",
            font=FONTS["heading"],
            text_color=COLORS["text"]["primary"]
        ).pack(side="left")
        
        # Main Content Area (Scrollable)
        content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=PADDING["medium"], pady=(0, PADDING["medium"]), sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Key Metrics Section
        self.create_key_metrics(content_frame)
        
        # Sales Analysis Section
        self.create_sales_analysis(content_frame)
        
        # Menu Performance Section
        self.create_menu_performance(content_frame)
        
        # Customer Insights Section
        self.create_customer_insights(content_frame)
        
        # Inventory Analysis Section
        self.create_inventory_analysis(content_frame)
    
    def create_key_metrics(self, parent):
        """Create the key metrics section."""
        # Section Title
        ctk.CTkLabel(
            parent,
            text="Key Business Metrics",
            font=FONTS["subheading"],
            text_color=COLORS["text"]["primary"]
        ).grid(row=0, column=0, pady=(0, PADDING["medium"]), sticky="w")
        
        # Metrics Grid
        metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        metrics_frame.grid(row=1, column=0, sticky="ew")
        metrics_frame.grid_columnconfigure((0,1,2), weight=1)
        
        # Create metric cards
        self.revenue_card = InsightCard(metrics_frame, "Total Revenue")
        self.revenue_card.grid(row=0, column=0, padx=(0, PADDING["small"]), sticky="ew")
        
        self.profit_card = InsightCard(metrics_frame, "Net Profit")
        self.profit_card.grid(row=0, column=1, padx=PADDING["small"], sticky="ew")
        
        self.orders_card = InsightCard(metrics_frame, "Total Orders")
        self.orders_card.grid(row=0, column=2, padx=(PADDING["small"], 0), sticky="ew")
    
    def create_sales_analysis(self, parent):
        """Create the sales analysis section."""
        # Section Title
        ctk.CTkLabel(
            parent,
            text="Sales Analysis",
            font=FONTS["subheading"],
            text_color=COLORS["text"]["primary"]
        ).grid(row=2, column=0, pady=(PADDING["large"], PADDING["medium"]), sticky="w")
        
        # Sales Chart
        chart_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        chart_frame.grid(row=3, column=0, sticky="ew")
        
        self.sales_figure = matplotlib.figure.Figure(figsize=(12, 6))
        self.sales_ax = self.sales_figure.add_subplot(111)
        self.sales_canvas = FigureCanvasTkAgg(self.sales_figure, master=chart_frame)
        self.sales_canvas.get_tk_widget().pack(padx=PADDING["medium"], pady=PADDING["medium"], fill="both", expand=True)
    
    def create_menu_performance(self, parent):
        """Create the menu performance section."""
        # Section Title
        ctk.CTkLabel(
            parent,
            text="Menu Performance",
            font=FONTS["subheading"],
            text_color=COLORS["text"]["primary"]
        ).grid(row=4, column=0, pady=(PADDING["large"], PADDING["medium"]), sticky="w")
        
        # Menu Charts Container
        menu_frame = ctk.CTkFrame(parent, fg_color="transparent")
        menu_frame.grid(row=5, column=0, sticky="ew")
        menu_frame.grid_columnconfigure((0,1), weight=1)
        
        # Top Items Chart
        top_items_frame = ctk.CTkFrame(menu_frame, fg_color="white", corner_radius=10)
        top_items_frame.grid(row=0, column=0, padx=(0, PADDING["small"]), sticky="ew")
        
        self.top_items_figure = matplotlib.figure.Figure(figsize=(6, 6))
        self.top_items_ax = self.top_items_figure.add_subplot(111)
        self.top_items_canvas = FigureCanvasTkAgg(self.top_items_figure, master=top_items_frame)
        self.top_items_canvas.get_tk_widget().pack(padx=PADDING["medium"], pady=PADDING["medium"], fill="both", expand=True)
        
        # Category Performance Chart
        category_frame = ctk.CTkFrame(menu_frame, fg_color="white", corner_radius=10)
        category_frame.grid(row=0, column=1, padx=(PADDING["small"], 0), sticky="ew")
        
        self.category_figure = matplotlib.figure.Figure(figsize=(6, 6))
        self.category_ax = self.category_figure.add_subplot(111)
        self.category_canvas = FigureCanvasTkAgg(self.category_figure, master=category_frame)
        self.category_canvas.get_tk_widget().pack(padx=PADDING["medium"], pady=PADDING["medium"], fill="both", expand=True)
    
    def create_customer_insights(self, parent):
        """Create the customer insights section."""
        # Section Title
        ctk.CTkLabel(
            parent,
            text="Customer Insights",
            font=FONTS["subheading"],
            text_color=COLORS["text"]["primary"]
        ).grid(row=6, column=0, pady=(PADDING["large"], PADDING["medium"]), sticky="w")
        
        # Insights Grid
        insights_frame = ctk.CTkFrame(parent, fg_color="transparent")
        insights_frame.grid(row=7, column=0, sticky="ew")
        insights_frame.grid_columnconfigure((0,1,2), weight=1)
        
        # Create insight cards
        self.avg_order_card = InsightCard(insights_frame, "Average Order Value")
        self.avg_order_card.grid(row=0, column=0, padx=(0, PADDING["small"]), sticky="ew")
        
        self.peak_hours_card = InsightCard(insights_frame, "Peak Hours")
        self.peak_hours_card.grid(row=0, column=1, padx=PADDING["small"], sticky="ew")
        
        self.table_usage_card = InsightCard(insights_frame, "Table Usage")
        self.table_usage_card.grid(row=0, column=2, padx=(PADDING["small"], 0), sticky="ew")
    
    def create_inventory_analysis(self, parent):
        """Create the inventory analysis section."""
        # Section Title
        ctk.CTkLabel(
            parent,
            text="Inventory Analysis",
            font=FONTS["subheading"],
            text_color=COLORS["text"]["primary"]
        ).grid(row=8, column=0, pady=(PADDING["large"], PADDING["medium"]), sticky="w")
        
        # Inventory Chart
        chart_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        chart_frame.grid(row=9, column=0, sticky="ew")
        
        self.inventory_figure = matplotlib.figure.Figure(figsize=(12, 6))
        self.inventory_ax = self.inventory_figure.add_subplot(111)
        self.inventory_canvas = FigureCanvasTkAgg(self.inventory_figure, master=chart_frame)
        self.inventory_canvas.get_tk_widget().pack(padx=PADDING["medium"], pady=PADDING["medium"], fill="both", expand=True)
    
    def update_key_metrics(self):
        """Update key business metrics."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Get current time in local timezone
            now = datetime.now(LOCAL_TZ)
            today = now.strftime('%Y-%m-%d')
            
            # Fetch total revenue
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0)
                FROM sales
                WHERE DATE(created_at, '+5 hours', '45 minutes', 'localtime') = ?
            """, (today,))
            revenue = cursor.fetchone()[0]
            
            # Fetch total expenses
            cursor.execute("""
                SELECT COALESCE(SUM(total_price), 0)
                FROM expenses
                WHERE DATE(expense_date, '+5 hours', '45 minutes', 'localtime') = ?
            """, (today,))
            expenses = cursor.fetchone()[0]
            
            # Calculate net profit
            profit = revenue - expenses
            
            # Fetch total orders
            cursor.execute("""
                SELECT COUNT(*)
                FROM sales
                WHERE DATE(created_at, '+5 hours', '45 minutes', 'localtime') = ?
            """, (today,))
            orders = cursor.fetchone()[0]
            
            # Update cards
            self.revenue_card.update(f"₹{revenue:,.2f}", "Today's Revenue")
            self.profit_card.update(f"₹{profit:,.2f}", "Today's Net Profit")
            self.orders_card.update(str(orders), "Orders Today")
            
        except Exception as e:
            print(f"Error updating key metrics: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def update_sales_chart(self):
        """Update sales analysis chart."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Fetch hourly sales data
            cursor.execute("""
                SELECT 
                    strftime('%I:%M %p', datetime(created_at, '+5 hours', '45 minutes', 'localtime')) as hour,
                    SUM(total_amount) as total_sales
                FROM sales
                WHERE DATE(created_at, '+5 hours', '45 minutes', 'localtime') = DATE('now', '+5 hours', '45 minutes', 'localtime')
                GROUP BY strftime('%H:%M', datetime(created_at, '+5 hours', '45 minutes', 'localtime'))
                ORDER BY created_at DESC
                LIMIT 12
            """)
            data = cursor.fetchall()
            
            if data:
                hours = [row[0] for row in data]
                sales = [float(row[1]) for row in data]
                
                # Clear previous plot
                self.sales_ax.clear()
                
                # Create gradient color
                gradient = self.sales_ax.fill_between(
                    range(len(hours)),
                    sales,
                    color='#3B82F6',
                    alpha=0.2
                )
                
                # Plot line with points
                self.sales_ax.plot(
                    range(len(hours)),
                    sales,
                    color='#3B82F6',
                    marker='o',
                    linewidth=2,
                    markersize=8
                )
                
                # Customize chart
                self.sales_ax.set_facecolor('white')
                self.sales_ax.grid(True, linestyle='--', alpha=0.3)
                self.sales_ax.set_title('Today\'s Sales Trend', pad=20)
                self.sales_ax.set_xlabel('Time')
                self.sales_ax.set_ylabel('Sales (₹)')
                
                # Set x-axis labels
                self.sales_ax.set_xticks(range(len(hours)))
                self.sales_ax.set_xticklabels(hours, rotation=45)
                
                # Update canvas
                self.sales_figure.tight_layout()
                self.sales_canvas.draw()
            
        except Exception as e:
            print(f"Error updating sales chart: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def update_menu_charts(self):
        """Update menu performance charts."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Fetch top selling items
            cursor.execute("""
                SELECT 
                    m.name,
                    COUNT(*) as order_count,
                    SUM(si.quantity) as total_quantity
                FROM sale_items si
                JOIN menu_items m ON si.menu_item_id = m.id
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.created_at, '+5 hours', '45 minutes', 'localtime') = DATE('now', '+5 hours', '45 minutes', 'localtime')
                GROUP BY m.id
                ORDER BY total_quantity DESC
                LIMIT 5
            """)
            items_data = cursor.fetchall()
            
            if items_data:
                # Clear previous plot
                self.top_items_ax.clear()
                
                # Prepare data
                items = [row[0] for row in items_data]
                quantities = [row[2] for row in items_data]
                
                # Create horizontal bar chart
                bars = self.top_items_ax.barh(
                    items,
                    quantities,
                    color='#3B82F6',
                    alpha=0.8
                )
                
                # Add value labels
                for bar in bars:
                    width = bar.get_width()
                    self.top_items_ax.text(
                        width,
                        bar.get_y() + bar.get_height()/2,
                        f'{int(width)}',
                        ha='left',
                        va='center',
                        fontweight='bold'
                    )
                
                # Customize chart
                self.top_items_ax.set_facecolor('white')
                self.top_items_ax.set_title('Top Selling Items', pad=20)
                self.top_items_ax.set_xlabel('Quantity Sold')
                
                # Update canvas
                self.top_items_figure.tight_layout()
                self.top_items_canvas.draw()
            
            # Fetch category performance
            cursor.execute("""
                SELECT 
                    COALESCE(mc.name, 'Other') as category,
                    COUNT(*) as order_count,
                    SUM(si.quantity * m.price) as revenue
                FROM sale_items si
                JOIN menu_items m ON si.menu_item_id = m.id
                LEFT JOIN menu_categories mc ON m.category_id = mc.id
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.created_at, '+5 hours', '45 minutes', 'localtime') = DATE('now', '+5 hours', '45 minutes', 'localtime')
                GROUP BY mc.id
                ORDER BY revenue DESC
            """)
            category_data = cursor.fetchall()
            
            if category_data:
                # Clear previous plot
                self.category_ax.clear()
                
                # Prepare data
                categories = [row[0] for row in category_data]
                revenue = [float(row[2]) for row in category_data]
                
                # Create pie chart
                self.category_ax.pie(
                    revenue,
                    labels=categories,
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=plt.cm.Pastel1(np.linspace(0, 1, len(categories)))
                )
                
                # Customize chart
                self.category_ax.set_title('Category Revenue Distribution', pad=20)
                
                # Update canvas
                self.category_figure.tight_layout()
                self.category_canvas.draw()
            
        except Exception as e:
            print(f"Error updating menu charts: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def update_customer_insights(self):
        """Update customer insight metrics."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Calculate average order value
            cursor.execute("""
                SELECT AVG(total_amount)
                FROM sales
                WHERE DATE(created_at, '+5 hours', '45 minutes', 'localtime') = DATE('now', '+5 hours', '45 minutes', 'localtime')
            """)
            avg_order = cursor.fetchone()[0] or 0
            
            # Find peak hours
            cursor.execute("""
                SELECT 
                    strftime('%H:00', datetime(created_at, '+5 hours', '45 minutes', 'localtime')) as hour,
                    COUNT(*) as order_count
                FROM sales
                WHERE DATE(created_at, '+5 hours', '45 minutes', 'localtime') = DATE('now', '+5 hours', '45 minutes', 'localtime')
                GROUP BY hour
                ORDER BY order_count DESC
                LIMIT 1
            """)
            peak_hour_data = cursor.fetchone()
            peak_hour = f"{peak_hour_data[0]} ({peak_hour_data[1]} orders)" if peak_hour_data else "No data"
            
            # Calculate table usage
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tables,
                    SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) as occupied_tables
                FROM tables
            """)
            table_data = cursor.fetchone()
            if table_data and table_data[0] > 0:
                usage_percent = (table_data[1] / table_data[0]) * 100
                table_usage = f"{usage_percent:.1f}%"
            else:
                table_usage = "No data"
            
            # Update cards
            self.avg_order_card.update(f"₹{avg_order:,.2f}", "Per Order Average")
            self.peak_hours_card.update(peak_hour, "Busiest Time Today")
            self.table_usage_card.update(table_usage, "Current Occupancy")
            
        except Exception as e:
            print(f"Error updating customer insights: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def update_inventory_chart(self):
        """Update inventory analysis chart."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Fetch inventory levels
            cursor.execute("""
                SELECT 
                    name,
                    remaining_quantity,
                    warning_level
                FROM bar_stock
                ORDER BY remaining_quantity ASC
                LIMIT 10
            """)
            data = cursor.fetchall()
            
            if data:
                # Clear previous plot
                self.inventory_ax.clear()
                
                # Prepare data
                items = [row[0] for row in data]
                quantities = [float(row[1]) for row in data]
                warnings = [float(row[2]) for row in data]
                
                # Create bar chart
                x = range(len(items))
                bar_width = 0.35
                
                self.inventory_ax.bar(
                    x,
                    quantities,
                    bar_width,
                    label='Current Stock',
                    color='#3B82F6'
                )
                
                self.inventory_ax.bar(
                    [i + bar_width for i in x],
                    warnings,
                    bar_width,
                    label='Warning Level',
                    color='#EF4444',
                    alpha=0.6
                )
                
                # Customize chart
                self.inventory_ax.set_facecolor('white')
                self.inventory_ax.set_title('Low Stock Items', pad=20)
                self.inventory_ax.set_xlabel('Items')
                self.inventory_ax.set_ylabel('Quantity')
                self.inventory_ax.set_xticks([i + bar_width/2 for i in x])
                self.inventory_ax.set_xticklabels(items, rotation=45, ha='right')
                self.inventory_ax.legend()
                
                # Update canvas
                self.inventory_figure.tight_layout()
                self.inventory_canvas.draw()
            
        except Exception as e:
            print(f"Error updating inventory chart: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def update_all(self):
        """Update all analytics components."""
        self.update_key_metrics()
        self.update_sales_chart()
        self.update_menu_charts()
        self.update_customer_insights()
        self.update_inventory_chart()
    
    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        self.update_all()
        self.after(5000, self.start_auto_refresh)  # Refresh every 5 seconds
    
    def destroy(self):
        """Clean up resources."""
        plt.close(self.sales_figure)
        plt.close(self.top_items_figure)
        plt.close(self.category_figure)
        plt.close(self.inventory_figure)
        super().destroy() 