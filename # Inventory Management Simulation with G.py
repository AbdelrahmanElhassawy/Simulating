# Inventory Management Simulation with GUI and PDF Auto-Analysis

# inventory_simulation_gui.py

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from datetime import datetime
import random
from tkinter import ttk, messagebox, filedialog
import tkinter as tk


class InventorySimulation:

    def __init__(self, root):

        self.root = root
        self.root.title("Inventory Management Simulation")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f4f4f4")

        self.report_data = []
        self.summary_results = {}

        self.create_variables()
        self.create_gui()

    def create_variables(self):

        self.initial_inventory = tk.IntVar(value=100)
        self.max_inventory = tk.IntVar(value=250)
        self.review_period = tk.IntVar(value=5)
        self.simulation_days = tk.IntVar(value=60)

        self.min_daily_demand = tk.IntVar(value=5)
        self.max_daily_demand = tk.IntVar(value=20)

        self.min_lead_time = tk.IntVar(value=1)
        self.max_lead_time = tk.IntVar(value=3)

        self.holding_cost = tk.DoubleVar(value=2.0)
        self.stockout_cost = tk.DoubleVar(value=10.0)

    def create_gui(self):

        title = tk.Label(
            self.root,
            text="Electronics Retail Store Inventory Simulation",
            font=("Arial", 18, "bold"),
            bg="#f4f4f4",
            fg="#003366"
        )
        title.pack(pady=10)

        input_frame = tk.LabelFrame(
            self.root,
            text="Simulation Parameters",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        input_frame.pack(fill="x", padx=15, pady=10)

        self.add_input(input_frame, "Initial Inventory:",
                       self.initial_inventory, 0)
        self.add_input(input_frame, "Maximum Inventory Level (M):",
                       self.max_inventory, 1)
        self.add_input(input_frame, "Review Period (N Days):",
                       self.review_period, 2)
        self.add_input(input_frame, "Simulation Days:",
                       self.simulation_days, 3)

        self.add_input(input_frame, "Minimum Daily Demand:",
                       self.min_daily_demand, 4)
        self.add_input(input_frame, "Maximum Daily Demand:",
                       self.max_daily_demand, 5)

        self.add_input(input_frame, "Minimum Lead Time:",
                       self.min_lead_time, 6)
        self.add_input(input_frame, "Maximum Lead Time:",
                       self.max_lead_time, 7)

        self.add_input(input_frame, "Holding Cost per Unit:",
                       self.holding_cost, 8)
        self.add_input(input_frame, "Stockout Cost per Unit:",
                       self.stockout_cost, 9)

        button_frame = tk.Frame(self.root, bg="#f4f4f4")
        button_frame.pack(pady=10)

        run_button = tk.Button(
            button_frame,
            text="Run Simulation",
            font=("Arial", 12, "bold"),
            bg="#007acc",
            fg="white",
            padx=20,
            pady=10,
            command=self.run_simulation
        )
        run_button.grid(row=0, column=0, padx=10)

        report_button = tk.Button(
            button_frame,
            text="Generate PDF Report",
            font=("Arial", 12, "bold"),
            bg="#28a745",
            fg="white",
            padx=20,
            pady=10,
            command=self.generate_pdf_report
        )
        report_button.grid(row=0, column=1, padx=10)

        self.tree = ttk.Treeview(
            self.root,
            columns=(
                "Day",
                "Demand",
                "Inventory",
                "OrderQty",
                "LeadTime",
                "Stockout",
                "HoldingCost",
                "StockoutCost"
            ),
            show="headings",
            height=20
        )

        headings = [
            "Day",
            "Demand",
            "Inventory",
            "OrderQty",
            "LeadTime",
            "Stockout",
            "HoldingCost",
            "StockoutCost"
        ]

        for heading in headings:
            self.tree.heading(heading, text=heading)
            self.tree.column(heading, width=120, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=15, pady=10)

        self.analysis_box = tk.Text(
            self.root,
            height=10,
            font=("Arial", 10)
        )
        self.analysis_box.pack(fill="x", padx=15, pady=10)

    def add_input(self, parent, text, variable, row):

        label = tk.Label(parent, text=text, font=("Arial", 10))
        label.grid(row=row, column=0, sticky="w", pady=5)

        entry = tk.Entry(parent, textvariable=variable, width=15)
        entry.grid(row=row, column=1, padx=10, pady=5)

    def run_simulation(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.analysis_box.delete("1.0", tk.END)
        self.report_data.clear()

        inventory = self.initial_inventory.get()
        M = self.max_inventory.get()
        N = self.review_period.get()
        days = self.simulation_days.get()

        min_demand = self.min_daily_demand.get()
        max_demand = self.max_daily_demand.get()

        min_lead = self.min_lead_time.get()
        max_lead = self.max_lead_time.get()

        holding_cost_rate = self.holding_cost.get()
        stockout_cost_rate = self.stockout_cost.get()

        total_holding_cost = 0
        total_stockout_cost = 0
        total_stockout_units = 0
        total_orders = 0
        stockout_days = 0

        pending_orders = []

        for day in range(1, days + 1):

            received_orders = []

            for order in pending_orders:
                order["remaining_days"] -= 1

                if order["remaining_days"] <= 0:
                    inventory += order["quantity"]
                    received_orders.append(order)

            pending_orders = [
                order for order in pending_orders
                if order not in received_orders
            ]

            demand = random.randint(min_demand, max_demand)

            stockout = 0

            if demand > inventory:
                stockout = demand - inventory
                total_stockout_units += stockout
                stockout_days += 1
                inventory = 0
            else:
                inventory -= demand

            order_quantity = 0
            lead_time = 0

            if day % N == 0:

                inventory_position = inventory + sum(
                    order["quantity"] for order in pending_orders
                )

                if inventory_position < M:
                    order_quantity = M - inventory_position
                    lead_time = random.randint(min_lead, max_lead)

                    pending_orders.append({
                        "quantity": order_quantity,
                        "remaining_days": lead_time
                    })

                    total_orders += 1

            holding_cost = inventory * holding_cost_rate
            stockout_cost = stockout * stockout_cost_rate

            total_holding_cost += holding_cost
            total_stockout_cost += stockout_cost

            row = (
                day,
                demand,
                inventory,
                order_quantity,
                lead_time,
                stockout,
                round(holding_cost, 2),
                round(stockout_cost, 2)
            )

            self.report_data.append(row)
            self.tree.insert("", tk.END, values=row)

        average_inventory = sum(row[2] for row in self.report_data) / days

        service_level = ((days - stockout_days) / days) * 100

        total_cost = total_holding_cost + total_stockout_cost

        self.summary_results = {
            "days": days,
            "review_period": N,
            "max_inventory": M,
            "total_orders": total_orders,
            "stockout_units": total_stockout_units,
            "average_inventory": round(average_inventory, 2),
            "holding_cost": round(total_holding_cost, 2),
            "stockout_cost": round(total_stockout_cost, 2),
            "total_cost": round(total_cost, 2),
            "service_level": round(service_level, 2)
        }

        analysis = self.generate_analysis_text()

        self.analysis_box.insert(tk.END, analysis)

        messagebox.showinfo(
            "Simulation Complete",
            "Inventory simulation completed successfully!"
        )

    def generate_analysis_text(self):

        results = self.summary_results

        analysis = "\n"
        analysis += "INVENTORY SYSTEM PERFORMANCE ANALYSIS\n"
        analysis += "=" * 60 + "\n\n"

        analysis += f"Simulation Period: {results['days']} days\n"
        analysis += f"Review Period (N): {results['review_period']} days\n"
        analysis += f"Maximum Inventory Level (M): {results['max_inventory']} units\n\n"

        analysis += "KEY PERFORMANCE INDICATORS\n"
        analysis += "-" * 40 + "\n"

        analysis += f"Service Level: {results['service_level']}%\n"
        analysis += f"Average Inventory Level: {results['average_inventory']} units\n"
        analysis += f"Total Orders Placed: {results['total_orders']}\n"
        analysis += f"Total Stockout Units: {results['stockout_units']}\n"
        analysis += f"Holding Cost: ${results['holding_cost']}\n"
        analysis += f"Stockout Cost: ${results['stockout_cost']}\n"
        analysis += f"Total System Cost: ${results['total_cost']}\n\n"

        analysis += "SYSTEM EVALUATION\n"
        analysis += "-" * 40 + "\n"

        if results['service_level'] >= 95:
            analysis += "Excellent service performance with minimal shortages.\n"
        elif results['service_level'] >= 85:
            analysis += "Good service level but there is still risk of shortages.\n"
        else:
            analysis += "Poor service level. Customers may frequently face stock unavailability.\n"

        if results['holding_cost'] > results['stockout_cost']:
            analysis += "Holding costs are relatively high compared to shortage costs.\n"
        else:
            analysis += "Shortage costs are dominating the system performance.\n"

        analysis += "\nRECOMMENDATIONS\n"
        analysis += "-" * 40 + "\n"

        if results['service_level'] < 90:
            analysis += "• Increase maximum inventory level (M) to reduce stockouts.\n"

        if results['review_period'] > 7:
            analysis += "• Reduce review period (N) to improve replenishment responsiveness.\n"

        if results['holding_cost'] > 5000:
            analysis += "• Reduce excess inventory to minimize holding costs.\n"

        if results['stockout_units'] > 0:
            analysis += "• Improve supplier coordination to reduce lead time uncertainty.\n"

        if results['service_level'] >= 95:
            analysis += "• Current policy is highly effective and stable.\n"

        analysis += "\nCONCLUSION\n"
        analysis += "-" * 40 + "\n"

        analysis += (
            "The simulation demonstrates how the periodic review inventory policy "
            "affects inventory availability, ordering behavior, and operational costs "
            "in an electronics retail environment. The balance between inventory level "
            "and review frequency is critical for improving customer satisfaction and "
            "minimizing total inventory cost.\n"
        )

        return analysis

    def generate_pdf_report(self):

        if not self.report_data:
            messagebox.showwarning(
                "No Simulation Data",
                "Please run the simulation first."
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not file_path:
            return

        doc = SimpleDocTemplate(file_path, pagesize=letter)

        styles = getSampleStyleSheet()
        elements = []

        title = Paragraph(
            "<b>Inventory Management Simulation Report</b>",
            styles['Title']
        )

        elements.append(title)
        elements.append(Spacer(1, 20))

        date_text = Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Normal']
        )

        elements.append(date_text)
        elements.append(Spacer(1, 20))

        summary_title = Paragraph(
            "<b>Simulation Summary</b>",
            styles['Heading2']
        )

        elements.append(summary_title)
        elements.append(Spacer(1, 10))

        summary = self.summary_results

        summary_data = [
            ["Metric", "Value"],
            ["Simulation Days", summary['days']],
            ["Review Period (N)", summary['review_period']],
            ["Maximum Inventory Level (M)", summary['max_inventory']],
            ["Total Orders", summary['total_orders']],
            ["Stockout Units", summary['stockout_units']],
            ["Average Inventory", summary['average_inventory']],
            ["Holding Cost", f"${summary['holding_cost']}"],
            ["Stockout Cost", f"${summary['stockout_cost']}"],
            ["Total Cost", f"${summary['total_cost']}"],
            ["Service Level", f"{summary['service_level']}%"]
        ]

        summary_table = Table(summary_data, colWidths=[250, 200])

        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 25))

        analysis_title = Paragraph(
            "<b>Automatic System Analysis</b>",
            styles['Heading2']
        )

        elements.append(analysis_title)
        elements.append(Spacer(1, 10))

        analysis_text = self.generate_analysis_text()

        analysis_paragraph = Paragraph(
            analysis_text.replace("\n", "<br/>"),
            styles['BodyText']
        )

        elements.append(analysis_paragraph)
        elements.append(Spacer(1, 25))

        elements.append(PageBreak())

        details_title = Paragraph(
            "<b>Daily Simulation Details</b>",
            styles['Heading2']
        )

        elements.append(details_title)
        elements.append(Spacer(1, 10))

        table_data = [[
            "Day",
            "Demand",
            "Inventory",
            "Order Qty",
            "Lead Time",
            "Stockout",
            "Holding Cost",
            "Stockout Cost"
        ]]

        for row in self.report_data:
            table_data.append(list(row))

        detail_table = Table(table_data, repeatRows=1)

        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))

        elements.append(detail_table)

        doc.build(elements)

        messagebox.showinfo(
            "PDF Report Generated",
            "The PDF analysis report was generated successfully!"
        )


if __name__ == "__main__":

    root = tk.Tk()
    app = InventorySimulation(root)
    root.mainloop()
