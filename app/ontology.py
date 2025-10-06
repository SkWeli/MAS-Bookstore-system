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
        class Stores(ObjectProperty):
            domain = [Inventory]; range = [Book]

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
        b1  = onto.Book("Book_HP1")
        b1.HasAuthor = "J. K. Rowling"
        b1.HasGenre  = "Fantasy"
        b1.HasPrice  = 1500.0
        b1.label     = ["Harry Potter and the Philosopher's Stone"]

        b2  = onto.Book("Book_1984")
        b2.HasAuthor = "George Orwell"
        b2.HasGenre  = "Dystopian"
        b2.HasPrice  = 1200.0
        b2.label     = ["Nineteen Eighty-Four"]

        b3  = onto.Book("Book_LOTR1")
        b3.HasAuthor = "J. R. R. Tolkien"
        b3.HasGenre  = "Fantasy"
        b3.HasPrice  = 1800.0
        b3.label     = ["The Fellowship of the Ring"]

        b4  = onto.Book("Book_LOTR2")
        b4.HasAuthor = "J. R. R. Tolkien"
        b4.HasGenre  = "Fantasy"
        b4.HasPrice  = 1800.0
        b4.label     = ["The Two Towers"]

        b5  = onto.Book("Book_LOTR3")
        b5.HasAuthor = "J. R. R. Tolkien"
        b5.HasGenre  = "Fantasy"
        b5.HasPrice  = 1800.0
        b5.label     = ["The Return of the King"]

        b6  = onto.Book("Book_DUNE")
        b6.HasAuthor = "Frank Herbert"
        b6.HasGenre  = "Sci-Fi"
        b6.HasPrice  = 1750.0
        b6.label     = ["Dune"]

        b7  = onto.Book("Book_HOBBIT")
        b7.HasAuthor = "J. R. R. Tolkien"
        b7.HasGenre  = "Fantasy"
        b7.HasPrice  = 1400.0
        b7.label     = ["The Hobbit"]

        b8  = onto.Book("Book_GATSBY")
        b8.HasAuthor = "F. Scott Fitzgerald"
        b8.HasGenre  = "Classic"
        b8.HasPrice  = 1100.0
        b8.label     = ["The Great Gatsby"]

        b9  = onto.Book("Book_MOBY")
        b9.HasAuthor = "Herman Melville"
        b9.HasGenre  = "Classic"
        b9.HasPrice  = 1300.0
        b9.label     = ["Moby-Dick"]

        b10 = onto.Book("Book_PRIDE")
        b10.HasAuthor = "Jane Austen"
        b10.HasGenre  = "Romance"
        b10.HasPrice  = 1250.0
        b10.label     = ["Pride and Prejudice"]

        b11 = onto.Book("Book_CATCHER")
        b11.HasAuthor = "J. D. Salinger"
        b11.HasGenre  = "Classic"
        b11.HasPrice  = 1200.0
        b11.label     = ["The Catcher in the Rye"]

        b12 = onto.Book("Book_MOCKING")
        b12.HasAuthor = "Harper Lee"
        b12.HasGenre  = "Classic"
        b12.HasPrice  = 1350.0
        b12.label     = ["To Kill a Mockingbird"]

        b13 = onto.Book("Book_BRAVE")
        b13.HasAuthor = "Aldous Huxley"
        b13.HasGenre  = "Dystopian"
        b13.HasPrice  = 1200.0
        b13.label     = ["Brave New World"]

        b14 = onto.Book("Book_ANIMAL")
        b14.HasAuthor = "George Orwell"
        b14.HasGenre  = "Satire"
        b14.HasPrice  = 1000.0
        b14.label     = ["Animal Farm"]

        b15 = onto.Book("Book_HHGTTG")
        b15.HasAuthor = "Douglas Adams"
        b15.HasGenre  = "Sci-Fi"
        b15.HasPrice  = 1450.0
        b15.label     = ["The Hitchhiker's Guide to the Galaxy"]

        b16 = onto.Book("Book_WARPEACE")
        b16.HasAuthor = "Leo Tolstoy"
        b16.HasGenre  = "Classic"
        b16.HasPrice  = 1600.0
        b16.label     = ["War and Peace"]

        b17 = onto.Book("Book_CRIME")
        b17.HasAuthor = "Fyodor Dostoevsky"
        b17.HasGenre  = "Classic"
        b17.HasPrice  = 1500.0
        b17.label     = ["Crime and Punishment"]

        b18 = onto.Book("Book_SCARLET")
        b18.HasAuthor = "Arthur Conan Doyle"
        b18.HasGenre  = "Mystery"
        b18.HasPrice  = 1150.0
        b18.label     = ["A Study in Scarlet"]

        b19 = onto.Book("Book_LILWOMEN")
        b19.HasAuthor = "Louisa May Alcott"
        b19.HasGenre  = "Classic"
        b19.HasPrice  = 1200.0
        b19.label     = ["Little Women"]

        b20 = onto.Book("Book_ALCHEMY")
        b20.HasAuthor = "Paulo Coelho"
        b20.HasGenre  = "Fiction"
        b20.HasPrice  = 1200.0
        b20.label     = ["The Alchemist"]

        #  Inventories 
        i1  = onto.Inventory("Inv_0001");  i1.AvailableQuantity = 50; i1.Stores = [b1]
        i2  = onto.Inventory("Inv_0002");  i2.AvailableQuantity = 20; i2.Stores = [b2]
        i3  = onto.Inventory("Inv_0003");  i3.AvailableQuantity = 25; i3.Stores = [b3]
        i4  = onto.Inventory("Inv_0004");  i4.AvailableQuantity = 22; i4.Stores = [b4]
        i5  = onto.Inventory("Inv_0005");  i5.AvailableQuantity = 22; i5.Stores = [b5]
        i6  = onto.Inventory("Inv_0006");  i6.AvailableQuantity = 24; i6.Stores = [b6]
        i7  = onto.Inventory("Inv_0007");  i7.AvailableQuantity = 28; i7.Stores = [b7]
        i8  = onto.Inventory("Inv_0008");  i8.AvailableQuantity = 26; i8.Stores = [b8]
        i9  = onto.Inventory("Inv_0009");  i9.AvailableQuantity = 18; i9.Stores = [b9]
        i10 = onto.Inventory("Inv_0010");  i10.AvailableQuantity = 27; i10.Stores = [b10]
        i11 = onto.Inventory("Inv_0011");  i11.AvailableQuantity = 23; i11.Stores = [b11]
        i12 = onto.Inventory("Inv_0012");  i12.AvailableQuantity = 25; i12.Stores = [b12]
        i13 = onto.Inventory("Inv_0013");  i13.AvailableQuantity = 21; i13.Stores = [b13]
        i14 = onto.Inventory("Inv_0014");  i14.AvailableQuantity = 30; i14.Stores = [b14]
        i15 = onto.Inventory("Inv_0015");  i15.AvailableQuantity = 20; i15.Stores = [b15]
        i16 = onto.Inventory("Inv_0016");  i16.AvailableQuantity = 16; i16.Stores = [b16]
        i17 = onto.Inventory("Inv_0017");  i17.AvailableQuantity = 18; i17.Stores = [b17]
        i18 = onto.Inventory("Inv_0018");  i18.AvailableQuantity = 22; i18.Stores = [b18]
        i19 = onto.Inventory("Inv_0019");  i19.AvailableQuantity = 24; i19.Stores = [b19]
        i20 = onto.Inventory("Inv_0020");  i20.AvailableQuantity = 26; i20.Stores = [b20]

        # People 
        e1 = onto.Employee("Emp_Alice")
        e2 = onto.Employee("Emp_Bob")

        c1  = onto.Customer("Cust_Maya")
        c2  = onto.Customer("Cust_Leo")
        c3  = onto.Customer("Cust_Ava")
        c4  = onto.Customer("Cust_Noah")
        c5  = onto.Customer("Cust_Ethan")
        c6  = onto.Customer("Cust_Aisha")
        c7  = onto.Customer("Cust_Sofia")
        c8  = onto.Customer("Cust_Kai")
        c9  = onto.Customer("Cust_Mia")
        c10 = onto.Customer("Cust_Arjun")
        c11 = onto.Customer("Cust_Li")
        c12 = onto.Customer("Cust_Zara")

        # Employees manage inventories (split 10/10)
        e1.WorksAt = [i1,i2,i3,i4,i5,i6,i7,i8,i9,i10]
        e2.WorksAt = [i11,i12,i13,i14,i15,i16,i17,i18,i19,i20]

        # Sample Purchases
        c1.Purchases  = [b1]     # Maya bought HP1
        c2.Purchases  = [b2]     # Leo bought 1984
        c3.Purchases  = [b3]
        c4.Purchases  = [b6]
        c5.Purchases  = [b7]
        c6.Purchases  = [b8]
        c7.Purchases  = [b10]
        c8.Purchases  = [b12]
        c9.Purchases  = [b14]
        c10.Purchases = [b15]
        c11.Purchases = [b19]
        c12.Purchases = [b20]

        o1 = onto.Order("Order_Maya_HP1");  o1.HasCustomer = [c1];  o1.HasBook = [b1]
        o2 = onto.Order("Order_Leo_1984");  o2.HasCustomer = [c2];  o2.HasBook = [b2]

    return onto
