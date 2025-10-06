from owlready2 import *

def add_rules(onto):
    with onto:
        inv_cls   = onto.Inventory
        low_cls   = onto.LowStock
        aq_prop   = onto.AvailableQuantity
        order_cls = onto.Order
        has_cust  = onto.HasCustomer
        has_book  = onto.HasBook
        purchases = onto.Purchases

        # Safety check 
        for name, ent in {
            "Inventory": inv_cls, "LowStock": low_cls, "AvailableQuantity": aq_prop,
            "Order": order_cls, "HasCustomer": has_cust, "HasBook": has_book, "Purchases": purchases
        }.items():
            assert ent is not None, f"{name} missing from ontology!"

        # Rule 1: AvailableQuantity < 10 - LowStock
        imp1 = Imp()
        imp1.set_as_rule(f"""
            {inv_cls.name}(?i), {aq_prop.name}(?i, ?q), lessThan(?q, 10)
            -> {low_cls.name}(?i)
        """)

        # Rule 2: Order(c,b) => Purchases(c,b)
        imp2 = Imp()
        imp2.set_as_rule(f"""
            {order_cls.name}(?o), {has_cust.name}(?o, ?c), {has_book.name}(?o, ?b)
            -> {purchases.name}(?c, ?b)
        """)
