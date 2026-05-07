# inventory_simulation_gui.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import csv
from datetime import datetime


class InventorySimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Electronics Store Inventory Simulation")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f4f4f4")

        self.create_variables()
        self.create_gui()

    def create_variables(self):
        self.initial_inventory = tk.IntVar(value=100)
        self.max_inventory = tk.IntVar(value=200)      # M
        self.review_period = tk.IntVar(value=5)        # N
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
            text="Inventory Management Simulation for Electronics Retail Store",
            font=("Arial", 18, "bold"),
            bg="#f4f4f4",
            fg="#003366"
        )
        title.pack(pady=10)

        input_frame = tk.LabelFrame(
            self.root,
            text="Simulation Parameters",
            padx=15,
            pady=15,
            font=("Arial", 11, "bold")
        )
        input_frame.pack(fill="x", padx=15, pady=10)

        self.add_input(input_frame, "Initial Inventory:",
                       self.initial_inventory, 0)
        self.add_input(input_frame, "Maximum Inventory Level (M):",
                       self.max_inventory, 1)
        self.add_input(input_frame, "Review Period (N days):",
                       self.review_period, 2)
        self.add_input(input_frame, "Simulation Days:",
                       self.simulation_days, 3)

        self.add_input(input_frame, "Min Daily Demand:",
                       self.min_daily_demand, 4)
        self.add_input(input_frame, "Max Daily Demand:",
                       self.max_daily_demand, 5)

        self.add_input(input_frame, "Min Lead Time:", self.min_lead_time, 6)
        self.add_input(input_frame, "Max Lead Time:", self.max_lead_time, 7)

        self.add_input(input_frame, "Holding Cost per Unit:",
                       self.holding_cost, 8)
        self.add_input(input_frame, "Stockout Cost per Unit:",
                       self.stockout_cost, 9)

        button_frame = tk.Frame(self.root, bg="#f4f4f4")
        button_frame.pack(pady=10)

        run_btn = tk.Button(
            button_frame,
            text="Run Simulation",
            font=("Arial", 12, "bold"),
            bg="#007acc",
            fg="white",
            padx=20,
            pady=10,
            command=self.run_simulation
        )
        run_btn.grid(row=0, column=0, padx=10)

        save_btn = tk.Button(
            button_frame,
            text="Save Report",
            font=("Arial", 12, "bold"),
            bg="#28a745",
            fg="white",
            padx=20,
            pady=10,
            command=self.save_report
        )
        save_btn.grid(row=0, column=1, padx=10)

        self.tree = ttk.Treeview(
            self.root,
            columns=(
                "Day",
                "Demand",
                "Inventory",
                "Order",
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
            "Order",
            "LeadTime",
            "Stockout",
            "HoldingCost",
            "StockoutCost"
        ]

        for heading in headings:
            self.tree.heading(heading, text=heading)
            self.tree.column(heading, width=120, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=15, pady=10)

        self.summary_text = tk.Text(self.root, height=8, font=("Arial", 10))
        self.summary_text.pack(fill="x", padx=15, pady=10)

        self.report_data = []

    def add_input(self, parent, text, variable, row):

        label = tk.Label(parent, text=text, font=("Arial", 10))
        label.grid(row=row, column=0, sticky="w", pady=5)

        entry = tk.Entry(parent, textvariable=variable, width=15)
        entry.grid(row=row, column=1, padx=10, pady=5)

    def run_simulation(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        self.summary_text.delete("1.0", tk.END)
        self.report_data.clear()

        inventory = self.initial_inventory.get()
        M = self.max_inventory.get()
        N = self.review_period.get()
        days = self.simulation_days.get()

        min_demand = self.min_daily_demand.get()
        max_demand = self.max_daily_demand.get()

        min_lead = self.min_lead_time.get()
        max_lead = self.max_lead_time.get()

        holding_cost_per_unit = self.holding_cost.get()
        stockout_cost_per_unit = self.stockout_cost.get()

        total_holding_cost = 0
        total_stockout_cost = 0
        total_stockouts = 0
        total_orders = 0

        pending_orders = []

        for day in range(1, days + 1):

            # Receive Orders
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

            # Daily Demand
            demand = random.randint(min_demand, max_demand)

            stockout = 0

            if demand > inventory:
                stockout = demand - inventory
                total_stockouts += stockout
                inventory = 0
            else:
                inventory -= demand

            # Periodic Review Policy
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

            # Costs
            holding_cost = inventory * holding_cost_per_unit
            stockout_cost = stockout * stockout_cost_per_unit

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

            self.tree.insert("", tk.END, values=row)
            self.report_data.append(row)

        avg_inventory = sum(row[2] for row in self.report_data) / days

        service_level = (
            ((days - len([r for r in self.report_data if r[5] > 0])) / days) * 100
        )

        summary = f"""
SIMULATION SUMMARY
==================================================

Total Simulation Days: {days}

Review Period (N): {N} days
Maximum Inventory Level (M): {M}

Total Orders Placed: {total_orders}

Total Stockout Units: {total_stockouts}

Average Inventory Level: {avg_inventory:.2f}

Total Holding Cost: ${total_holding_cost:.2f}

Total Stockout Cost: ${total_stockout_cost:.2f}

Service Level: {service_level:.2f}%

RECOMMENDATIONS
==================================================
"""

        # Recommendations
        if service_level < 90:
            summary += "\n- Increase maximum inventory level (M) to reduce stockouts."

        if total_holding_cost > total_stockout_cost:
            summary += "\n- Reduce inventory level to lower holding costs."

        if N > 7:
            summary += "\n- Reduce review period (N) for faster replenishment."

        if service_level >= 95:
            summary += "\n- Current inventory policy performs efficiently."

        self.summary_text.insert(tk.END, summary)

        messagebox.showinfo("Simulation Complete",
                            "Inventory simulation completed successfully!")

    def save_report(self):

        if not self.report_data:
            messagebox.showwarning(
                "No Data", "Please run the simulation first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not file_path:
            return

        with open(file_path, mode="w", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Day",
                "Demand",
                "Inventory",
                "OrderQuantity",
                "LeadTime",
                "Stockout",
                "HoldingCost",
                "StockoutCost"
            ])

            for row in self.report_data:
                writer.writerow(row)

        report_name = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_name, "w") as report:
            report.write(self.summary_text.get("1.0", tk.END))

        messagebox.showinfo(
            "Report Saved",
            f"CSV report saved successfully.\nSummary report saved as:\n{report_name}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = InventorySimulation(root)
    root.mainloop()
