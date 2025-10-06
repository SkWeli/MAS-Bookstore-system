from model import BookstoreModel

if __name__ == "__main__":
    m = BookstoreModel(n_customers=12, n_employees=2, steps=40, seed=42, restock_threshold=10, restock_target=30)
    m.run()
    print("Simulation complete. Ontology saved to bms_result.owl")
