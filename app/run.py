from model import BookstoreModel

if __name__ == "__main__":
    m = BookstoreModel(n_customers=3, n_employees=1, steps=40, seed=42)
    m.run()
    print("Simulation complete. Ontology saved to bms_result.owl")
