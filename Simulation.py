import random
import pandas as pd
import io


# ==========================================
# 1. Data Class: DailyRecord
# ==========================================
class DailyRecord:
    def __init__(self, day_id, day_type, rand_demand, demand, rented, idle,
                 extra_demand, cost, revenue, salvage, lost_profit, profit):
        self.day_id = day_id
        self.day_type = day_type
        self.rand_demand = rand_demand
        self.demand = demand
        self.rented = rented
        self.idle = idle
        self.extra_demand = extra_demand
        self.cost = cost
        self.revenue = revenue
        self.salvage = salvage
        self.lost_profit = lost_profit
        self.profit = profit


# ==========================================
# 2. Configuration Class: SimulationConfig
# ==========================================
class SimulationConfig:
    def __init__(self, capacity, cost_per_server, selling_price, salvage_value,
                 good_pct, fair_pct, poor_pct, num_days):
        self.capacity = capacity
        self.cost_per_server = cost_per_server
        self.selling_price = selling_price
        self.salvage_value = salvage_value
        self.num_days = num_days

        self.day_types = [
            (good_pct, 'Good'),
            (good_pct + fair_pct, 'Fair'),
            (100, 'Poor')
        ]

        self.demand_mappings = {}
        self.load_demand_probabilities()

    def load_demand_probabilities(self):
        self.demand_mappings = {
            'Good': [(10, 40), (28, 50), (43, 60), (63, 70), (98, 80), (100, 90)],
            'Fair': [(15, 40), (35, 50), (75, 60), (90, 70), (98, 80), (100, 90)],
            'Poor': [(44, 40), (66, 50), (82, 60), (94, 70), (100, 80)]
        }


# ==========================================
# 3. Core Engine: SimulationEngine
# ==========================================
class SimulationEngine:
    def __init__(self, config):
        self.config = config

    def _get_random_value(self, mapping_list):
        rand_num = random.randint(1, 100)
        for boundary, value in mapping_list:
            if rand_num <= boundary:
                return value, rand_num
        return mapping_list[-1][1], rand_num

    def calculate_daily_math(self, day_id, day_type, rand_demand, demand):
        rented = min(demand, self.config.capacity)
        idle = max(0, self.config.capacity - demand)
        extra_demand = max(0, demand - self.config.capacity)

        lost_profit_per_unit = self.config.selling_price - self.config.cost_per_server
        lost_profit = extra_demand * lost_profit_per_unit

        cost = self.config.capacity * self.config.cost_per_server
        revenue = rented * self.config.selling_price
        salvage_revenue = idle * self.config.salvage_value

        net_profit = revenue - cost - lost_profit + salvage_revenue

        return DailyRecord(
            day_id, day_type, rand_demand, demand, rented, idle,
            extra_demand, cost, revenue, salvage_revenue, lost_profit, net_profit
        )

    def run_simulation(self):
        results = []

        for day in range(1, self.config.num_days + 1):
            day_type, _ = self._get_random_value(self.config.day_types)
            demand, rand_demand = self._get_random_value(self.config.demand_mappings[day_type])

            record = self.calculate_daily_math(day, day_type, rand_demand, demand)
            results.append(record)

        return results


# ==========================================
# 4. Convert Results to DataFrame
# ==========================================
def results_to_dataframe(results):
    data = []

    for r in results:
        data.append({
            "Day": r.day_id,
            "Day Type": r.day_type,
            "RND": r.rand_demand,
            "Demand": r.demand,
            "Rented": r.rented,
            "Idle": r.idle,
            "Extra Demand": r.extra_demand,
            "Total Cost": r.cost,
            "Rental Revenue": r.revenue,
            "Salvage Revenue": r.salvage,
            "Lost Profit": r.lost_profit,
            "Net Profit": r.profit
        })

    df = pd.DataFrame(data)

    if not df.empty:
        df["Cumulative Profit"] = df["Net Profit"].cumsum()

    return df


# ==========================================
# 5. Convert Results to JSON-Friendly Dict
# ==========================================
def results_to_list(results):
    output = []

    for r in results:
        output.append({
            "day": r.day_id,
            "day_type": r.day_type,
            "rnd": r.rand_demand,
            "demand": r.demand,
            "rented": r.rented,
            "idle": r.idle,
            "extra_demand": r.extra_demand,
            "total_cost": round(r.cost, 2),
            "rental_revenue": round(r.revenue, 2),
            "salvage_revenue": round(r.salvage, 2),
            "lost_profit": round(r.lost_profit, 2),
            "net_profit": round(r.profit, 2)
        })

    return output


# ==========================================
# 6. Create Summary
# ==========================================
def create_summary(results):
    total_profit = 0
    total_rented = 0
    total_idle = 0
    total_extra = 0
    total_cost = 0
    total_revenue = 0
    total_salvage = 0
    total_lost = 0

    for r in results:
        total_profit += r.profit
        total_rented += r.rented
        total_idle += r.idle
        total_extra += r.extra_demand
        total_cost += r.cost
        total_revenue += r.revenue
        total_salvage += r.salvage
        total_lost += r.lost_profit

    return {
        "total_servers_rented": total_rented,
        "total_idle_servers": total_idle,
        "total_extra_demand": total_extra,
        "total_rental_revenue": round(total_revenue, 2),
        "total_server_cost": round(total_cost, 2),
        "total_salvage_revenue": round(total_salvage, 2),
        "total_lost_profit": round(total_lost, 2),
        "final_net_profit": round(total_profit, 2)
    }


# ==========================================
# 7. Prepare Chart Data
# ==========================================
def create_chart_data(df):
    if df.empty:
        return {
            "days": [],
            "net_profit": [],
            "cumulative_profit": [],
            "demand": [],
            "rented": []
        }

    return {
        "days": df["Day"].tolist(),
        "net_profit": df["Net Profit"].tolist(),
        "cumulative_profit": df["Cumulative Profit"].tolist(),
        "demand": df["Demand"].tolist(),
        "rented": df["Rented"].tolist()
    }


# ==========================================
# 8. Main Function for API
# ==========================================
def run_simulation_api(data):
    capacity = int(data["capacity"])
    cost_per_server = float(data["cost_per_server"])
    selling_price = float(data["selling_price"])
    salvage_value = float(data["salvage_value"])
    good_pct = int(data["good_pct"])
    fair_pct = int(data["fair_pct"])
    poor_pct = int(data["poor_pct"])
    num_days = int(data["num_days"])

    if good_pct + fair_pct + poor_pct != 100:
        raise ValueError("Good + Fair + Poor percentages must equal 100.")

    config = SimulationConfig(
        capacity=capacity,
        cost_per_server=cost_per_server,
        selling_price=selling_price,
        salvage_value=salvage_value,
        good_pct=good_pct,
        fair_pct=fair_pct,
        poor_pct=poor_pct,
        num_days=num_days
    )

    engine = SimulationEngine(config)
    results = engine.run_simulation()

    df = results_to_dataframe(results)

    return {
        "results": results_to_list(results),
        "summary": create_summary(results),
        "charts": create_chart_data(df)
    }


# ==========================================
# 9. Generate Excel File from Displayed Data
# ==========================================
def generate_excel_file(results, summary):
    results_df = pd.DataFrame(results)

    if not results_df.empty:
        rename_map = {
            "day": "Day",
            "day_type": "Day Type",
            "rnd": "RND",
            "demand": "Demand",
            "rented": "Rented",
            "idle": "Idle",
            "extra_demand": "Extra Demand",
            "total_cost": "Total Cost",
            "rental_revenue": "Rental Revenue",
            "salvage_revenue": "Salvage Revenue",
            "lost_profit": "Lost Profit",
            "net_profit": "Net Profit"
        }

        results_df = results_df.rename(columns=rename_map)

        ordered_columns = [
            "Day",
            "Day Type",
            "RND",
            "Demand",
            "Rented",
            "Idle",
            "Extra Demand",
            "Total Cost",
            "Rental Revenue",
            "Salvage Revenue",
            "Lost Profit",
            "Net Profit"
        ]

        results_df = results_df[[col for col in ordered_columns if col in results_df.columns]]

        if "Net Profit" in results_df.columns:
            results_df["Cumulative Profit"] = results_df["Net Profit"].cumsum()

    summary_rows = []
    summary = summary or {}

    summary_map = {
        "total_servers_rented": "Total Servers Rented",
        "total_idle_servers": "Total Idle Servers",
        "total_extra_demand": "Total Extra Demand",
        "total_rental_revenue": "Total Rental Revenue",
        "total_server_cost": "Total Server Cost",
        "total_salvage_revenue": "Total Salvage Revenue",
        "total_lost_profit": "Total Lost Profit",
        "final_net_profit": "Final Net Profit"
    }

    for key, label in summary_map.items():
        summary_rows.append({
            "Metric": label,
            "Value": summary.get(key, 0)
        })

    summary_df = pd.DataFrame(summary_rows)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        results_df.to_excel(writer, sheet_name="Daily Results", index=False)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

    output.seek(0)
    return output