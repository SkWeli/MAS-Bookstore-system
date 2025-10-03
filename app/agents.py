import random
from mesa import Agent
from owlready2 import sync_reasoner
from messaging import TOPIC_PURCHASE_REQ, TOPIC_RESTOCK_REQ, TOPIC_PURCHASE_OK, TOPIC_PURCHASE_FAIL

class CustomerAgent(Agent):
    def __init__(self, unique_id, model, onto, bus):
        super().__init__(unique_id, model)
        self.onto = onto; self.bus = bus
        self.purchased = []

    def step(self):
        # pick a random book individual
        book = random.choice(list(self.onto.Book.instances()))
        qty = 1
        self.bus.publish(TOPIC_PURCHASE_REQ, {
            "customer_id": self.unique_id,
            "book_iri": book.iri,
            "qty": qty
        })

class EmployeeAgent(Agent):
    def __init__(self, unique_id, model, onto, bus):
        super().__init__(unique_id, model)
        self.onto = onto; self.bus = bus
        bus.subscribe(TOPIC_RESTOCK_REQ, self.handle_restock)

    def handle_restock(self, payload):
        inv_iri = payload["inventory_iri"]; qty = payload["qty"]
        inv = self.onto.search_one(iri=inv_iri)
        inv.AvailableQuantity = [int(inv.AvailableQuantity[0]) + qty]

    def step(self):
        # Employees periodically run a reasoner pass; if any LowStock, restock
        sync_reasoner(self.onto, infer_property_values=True)
        low = list(self.onto.LowStock.instances())
        for inv in low:
            # restock to target level
            target = 5
            add = max(0, target - int(inv.AvailableQuantity[0]))
            if add > 0:
                self.bus.publish(TOPIC_RESTOCK_REQ, {"inventory_iri": inv.iri, "qty": add})

class InventoryManager:
    """Stateless handlers that update ontology for purchases (not a Mesa Agent)."""
    def __init__(self, onto, bus):
        self.onto = onto; self.bus = bus
        bus.subscribe(TOPIC_PURCHASE_REQ, self.handle_purchase)

    def handle_purchase(self, payload):
        onto = self.onto
        book = onto.search_one(iri=payload["book_iri"])
        # Find inventory matching this book by naming convention (Inv_<bookname>)
        inv = onto.search_one(Inventory, iri=book.iri.replace("Book_", "Inv_"))
        qty_avail = int(inv.AvailableQuantity[0])
        if qty_avail >= payload["qty"]:
            # Create an Order individual to trigger SWRL Purchases inference
            o = onto.Order(f"Order_{payload['customer_id']}_{book.name}_{self._rand()}")
            cust = self._customer_from_id(payload["customer_id"])
            onto.HasCustomer[o] = [cust]
            onto.HasBook[o] = [book]

            inv.AvailableQuantity = [qty_avail - payload["qty"]]
            self.bus.publish(TOPIC_PURCHASE_OK, payload)
        else:
            self.bus.publish(TOPIC_PURCHASE_FAIL, payload)

    def _customer_from_id(self, cid):
        # Customers are created with IDs like Cust_1 etc. We stored their IRI in model init.
        return next(iter(self.onto.Customer.instances()))

    def _rand(self):
        import random, string
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
