import random
from mesa import Agent
from messaging import TOPIC_PURCHASE_REQ, TOPIC_RESTOCK_REQ, TOPIC_PURCHASE_OK, TOPIC_PURCHASE_FAIL

def _title(book_ind):
    # Use rdfs:label if present; otherwise fall back to the name
    labels = getattr(book_ind, "label", [])
    return labels[0] if labels else book_ind.name

class CustomerAgent(Agent):
    def __init__(self, unique_id, model, onto, bus):
        super().__init__(unique_id, model)
        self.onto = onto
        self.bus = bus
        self.purchased = []

    def step(self):
        # pick a random book individual
        book = random.choice(list(self.onto.Book.instances()))
        qty = random.randint(1, 5)
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
        emps = list(self.onto.Employee.instances())
        try:
            idx = int(str(unique_id).split("_")[-1]) - 1  # Emp_1 -> 0
        except Exception:
            idx = 0
        self.person = emps[idx % len(emps)] if emps else None
        self.managed = set(getattr(self.person, "WorksAt", []))  # inventories this employee owns
        bus.subscribe(TOPIC_RESTOCK_REQ, self.handle_restock)

    def handle_restock(self, payload):
        # read directly from payload (no stray var names)
        iri = payload["inventory_iri"]
        qty = int(payload["qty"])

        inv = self.onto.search_one(iri=iri)
        if inv is None:
            return  # unknown inventory; ignore safely

        # if you added routing by WorksAt, ignore inventories I don't own
        if hasattr(self, "managed") and self.managed and (inv not in self.managed):
            return

        # pretty title for logging
        book  = (getattr(inv, "Stores", []) or [None])[0]
        title = _title(book) if book else inv.name
        who   = getattr(self, "person", None).name if getattr(self, "person", None) else self.unique_id

        inv.AvailableQuantity = int(inv.AvailableQuantity) + qty
        print(f"[RESTOCK] {who} restocked {title} +{qty} → {int(inv.AvailableQuantity)}")

        # optional: log to events for your CSV/dashboard
        if hasattr(self.model, "events"):
            self.model.events.append({
                "step": self.model.step_idx,
                "type": "restock",
                "employee": who,
                "inventory": inv.name,
                "book": title,
                "qty": qty,
                "after_qty": int(inv.AvailableQuantity),
            })


    def step(self):
        threshold = getattr(self.model, "restock_threshold", 10)
        target    = getattr(self.model, "restock_target", 30)
        for inv in list(self.managed):  # ← only inventories this employee manages
            q = int(inv.AvailableQuantity)
            if q < threshold:
                add = target - q
                if add > 0:
                    self.bus.publish(TOPIC_RESTOCK_REQ, {"inventory_iri": inv.iri, "qty": add})

class BookAgent(Agent):
    def __init__(self, unique_id, model, onto, book_individual):
        super().__init__(unique_id, model)
        self.onto = onto
        self.book = book_individual
        # Resolve its inventory via Stores inverse (Inventory -> Stores -> Book)
        # We assume 1-to-1 inventory per book in this toy model.
        self.inventory = next((inv for inv in onto.Inventory.instances()
                               if self.book in getattr(inv, "Stores", [])), None)

    @property
    def title(self):
        return self.book.name

    @property
    def author(self):
        return str(getattr(self.book, "HasAuthor", ""))

    @property
    def genre(self):
        return str(getattr(self.book, "HasGenre", ""))

    @property
    def price(self):
        return float(getattr(self.book, "HasPrice", 0.0))

    @property
    def stock(self):
        return int(getattr(self.inventory, "AvailableQuantity", 0)) if self.inventory else 0

    def step(self):
        # Passive (no action needed). Exists to satisfy spec & for potential future behaviors.
        pass

class InventoryManager:
    """Handles purchases; not a Mesa Agent."""

    def __init__(self, onto, bus):
        self.onto = onto
        self.bus = bus
        bus.subscribe(TOPIC_PURCHASE_REQ, self.handle_purchase)

    def handle_purchase(self, payload):
        onto = self.onto
        book = onto.search_one(iri=payload["book_iri"])
        inv = onto.search_one(type=onto.Inventory, Stores=book)
        if not inv:
            # fallback (very unlikely): scan
            inv = next((x for x in onto.Inventory.instances() if book in getattr(x, "Stores", [])), None)

        if not inv:
            raise RuntimeError(f"No Inventory found for book {book.name}")
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
            title = _title(book)
            print(
                f"[OK] {cust.name} bought 1x {title}. New qty: {int(inv.AvailableQuantity)}"
            )
            self.bus.publish(TOPIC_PURCHASE_OK, payload)
        else:
            print(
                f"[FAIL] Not enough stock for {book.name} (have {qty_avail})"
            )
            self.bus.publish(TOPIC_PURCHASE_FAIL, payload)

    def _customer_from_id(self, cid):
        # Map agent ids like "Cust_1", "Cust_2", ... to ontology customers in order.
        try:
            idx = int(str(cid).split("_")[-1]) - 1
        except Exception:
            idx = 0
        customers = sorted(self.onto.Customer.instances(), key=lambda x: x.name)
        if not customers:
            raise RuntimeError("No Customer individuals found in ontology.")
        return customers[idx % len(customers)]

    def _rand(self):
        import string
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
