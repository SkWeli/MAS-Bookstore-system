from mesa import Model
from mesa.time import RandomActivation
from ontology import build_ontology, seed_data
from rules import add_rules
from agents import CustomerAgent, EmployeeAgent, InventoryManager
from messaging import MessageBus

import csv
from pathlib import Path

class BookstoreModel(Model):
    def __init__(self, n_customers=3, n_employees=1, steps=30, seed=None):
        super().__init__(seed=seed)
        self.steps = steps
        self.schedule = RandomActivation(self)
        self.bus = MessageBus()

        self.events = []   # per-event rows: {"step": int, "type": ..., "book": ..., "qty": int}
        self.ts = []       # per-step snapshots: {"step": int, "Inv_HP1": int, "Inv_1984": int}
        self.step_idx = 0

        # Ontology
        self.onto = build_ontology()
        seed_data(self.onto)
        add_rules(self.onto)
        self.inv_manager = InventoryManager(self.onto, self.bus)

        # Agents
        for i in range(n_customers):
            a = CustomerAgent(f"Cust_{i+1}", self, self.onto, self.bus)
            self.schedule.add(a)
        for j in range(n_employees):
            e = EmployeeAgent(f"Emp_{j+1}", self, self.onto, self.bus)
            self.schedule.add(e)

        self._snapshot()

    def _snapshot(self):
        # capture all Inventory quantities by name for the dashboard
        row = {"step": self.step_idx}
        for inv in self.onto.Inventory.instances():
            # friendly col name: use the individual name
            row[inv.name] = int(inv.AvailableQuantity)
        self.ts.append(row)

    def step(self):
        self.schedule.step()
        self.step_idx += 1
        self._snapshot()

    def run(self):
        for _ in range(self.steps):
            self.step()
        # save ontology snapshot for inspection
        self.onto.save(file="bms_result.owl", format="rdfxml")

        Path("report").mkdir(parents=True, exist_ok=True)

        # events
        if self.events:
            with open("report/events.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=sorted(set().union(*[e.keys() for e in self.events])))
                writer.writeheader()
                writer.writerows(self.events)

        # time series
        if self.ts:
            # normalize columns for consistent header
            all_keys = sorted(set().union(*[r.keys() for r in self.ts]))
            with open("report/inventory_timeseries.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=all_keys)
                writer.writeheader()
                writer.writerows(self.ts)