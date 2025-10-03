from mesa import Model
from mesa.time import RandomActivation
from ontology import build_ontology, seed_data
from rules import add_rules
from agents import CustomerAgent, EmployeeAgent, InventoryManager
from messaging import MessageBus

class BookstoreModel(Model):
    def __init__(self, n_customers=3, n_employees=1, steps=30, seed=None):
        super().__init__(seed=seed)
        self.steps = steps
        self.schedule = RandomActivation(self)
        self.bus = MessageBus()

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

    def step(self):
        self.schedule.step()

    def run(self):
        for _ in range(self.steps):
            self.step()
        # save ontology snapshot for inspection
        self.onto.save(file="bms_result.owl", format="rdfxml")
