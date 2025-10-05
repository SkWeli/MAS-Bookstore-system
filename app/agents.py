import random
from mesa import Agent
from messaging import TOPIC_PURCHASE_REQ, TOPIC_RESTOCK_REQ, TOPIC_PURCHASE_OK, TOPIC_PURCHASE_FAIL


class CustomerAgent(Agent):
    def __init__(self, unique_id, model, onto, bus):
        super().__init__(unique_id, model)
        self.onto = onto
        self.bus = bus
        self.purchased = []

    def step(self):
        # pick a random book individual
        book = random.choice(list(self.onto.Book.instances()))
        qty = 1
        self.model.events.append({"step": self.model.step_idx, "type": "purchase_request", "customer": self.unique_id, "book": book.name, "qty": qty})
        self.bus.publish(
            TOPIC_PURCHASE_REQ,
            {"customer_id": self.unique_id, "book_iri": book.iri, "qty": qty},
        )


class EmployeeAgent(Agent):
    def __init__(self, unique_id, model, onto, bus):
        super().__init__(unique_id, model)
        self.onto = onto
        self.bus = bus
        bus.subscribe(TOPIC_RESTOCK_REQ, self.handle_restock)

    def handle_restock(self, payload):
        inv_iri = payload["inventory_iri"]
        qty = payload["qty"]
        inv = self.onto.search_one(iri=inv_iri)
        inv.AvailableQuantity = int(inv.AvailableQuantity) + qty
        print(f"[RESTOCK] {inv.name} +{qty} → {int(inv.AvailableQuantity)}")
        self.model.events.append({"step": self.model.step_idx, "type": "restock", "inventory": inv.name, "qty": qty, "after_qty": int(inv.AvailableQuantity)})


    def step(self):
        # Python fallback: check directly for low stock (<3) and trigger restock
        for inv in list(self.onto.Inventory.instances()):
            q = int(inv.AvailableQuantity)
            if q < 3:
                add = 5 - q
                if add > 0:
                    self.bus.publish(
                        TOPIC_RESTOCK_REQ, {"inventory_iri": inv.iri, "qty": add}
                    )


class InventoryManager:
    """Handles purchases; not a Mesa Agent."""

    def __init__(self, onto, bus):
        self.onto = onto
        self.bus = bus
        bus.subscribe(TOPIC_PURCHASE_REQ, self.handle_purchase)

    def handle_purchase(self, payload):
        onto = self.onto
        book = onto.search_one(iri=payload["book_iri"])
        inv = onto.search_one(
            type=onto.Inventory, iri=book.iri.replace("Book_", "Inv_")
        )
        qty_avail = int(inv.AvailableQuantity)

        if qty_avail >= payload["qty"]:
            # Create an Order individual for ontology consistency
            o = onto.Order(
                f"Order_{payload['customer_id']}_{book.name}_{self._rand()}"
            )
            cust = self._customer_from_id(payload["customer_id"])
            o.HasCustomer = [cust]
            o.HasBook = [book]

            # Directly assert Purchases relation
            current = list(getattr(cust, "Purchases", []))
            cust.Purchases = current + [book]

            inv.AvailableQuantity = qty_avail - payload["qty"]
            print(
                f"[OK] {cust.name} bought 1x {book.name}. New qty: {int(inv.AvailableQuantity)}"
            )
            self.bus.publish(TOPIC_PURCHASE_OK, payload)
        else:
            print(
                f"[FAIL] Not enough stock for {book.name} (have {qty_avail})"
            )
            self.bus.publish(TOPIC_PURCHASE_FAIL, payload)

    def _customer_from_id(self, cid):
        return next(iter(self.onto.Customer.instances()))

    def _rand(self):
        import string
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
