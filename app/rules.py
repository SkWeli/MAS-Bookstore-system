from owlready2 import *

def add_rules(onto):
    with onto:
        # Low-stock: Inventory with AvailableQuantity < 3 -> mark as LowStock
        # Note: Owlready2 supports SWRL with swrlb: built-ins.
        imp1 = Imp()
        imp1.set_as_rule("""
            Inventory(?i), AvailableQuantity(?i, ?q), swrlb:lessThan(?q, 3)
            -> LowStock(?i)
        """)

        # Purchase tag: If an Order links a Customer and Book => Purchases(Customer, Book)
        imp2 = Imp()
        imp2.set_as_rule("""
            Order(?o), HasCustomer(?o, ?c), HasBook(?o, ?b)
            -> Purchases(?c, ?b)
        """)
