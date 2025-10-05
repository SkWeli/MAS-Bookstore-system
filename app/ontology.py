from owlready2 import *

def build_ontology():
    onto = get_ontology("http://example.org/bms.owl")
    with onto:
        # Classes
        class Book(Thing): pass
        class Customer(Thing): pass
        class Employee(Thing): pass
        class Order(Thing): pass
        class Inventory(Thing): pass

        # Inferred/tagging classes (used by rules)
        class LowStock(Inventory): pass
        class RestockRequested(Inventory): pass

        # Object properties
        class Purchases(ObjectProperty):
            domain = [Customer]; range = [Book]
        class WorksAt(ObjectProperty):
            domain = [Employee]; range = [Inventory]
        class HasBook(ObjectProperty):
            domain = [Order]; range = [Book]
        class HasCustomer(ObjectProperty):
            domain = [Order]; range = [Customer]

        # Data properties
        class HasAuthor(DataProperty, FunctionalProperty):
            domain = [Book]; range = [str]
        class HasGenre(DataProperty, FunctionalProperty):
            domain = [Book]; range = [str]
        class HasPrice(DataProperty, FunctionalProperty):
            domain = [Book]; range = [float]
        class AvailableQuantity(DataProperty, FunctionalProperty):
            domain = [Inventory]; range = [int]

    return onto

def seed_data(onto):
    with onto:
        # Books
        b1 = onto.Book("Book_HP1")
        b1.HasAuthor = "J. K. Rowling"   # functional
        b1.HasGenre  = "Fantasy"       # non-functional (use list or .append)
        b1.HasPrice  = 15.0

        b2 = onto.Book("Book_1984")
        b2.HasAuthor = "George Orwell"
        b2.HasGenre  = "Dystopian"
        b2.HasPrice  = 12.0

        # Inventory
        i1 = onto.Inventory("Inv_HP1");  i1.AvailableQuantity = 5
        i2 = onto.Inventory("Inv_1984"); i2.AvailableQuantity = 2

        # People
        e1 = onto.Employee("Emp_Alice"); e2 = onto.Employee("Emp_Bob")
        c1 = onto.Customer("Cust_Maya"); c2 = onto.Customer("Cust_Leo")

        # Object property assignments go on instances
        e1.WorksAt = [i1]
        e2.WorksAt = [i2]
    return onto
