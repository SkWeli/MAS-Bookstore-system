from collections import defaultdict

class MessageBus:
    def __init__(self):
        self.subs = defaultdict(list)

    def subscribe(self, topic, handler):
        self.subs[topic].append(handler)

    def publish(self, topic, payload):
        for h in list(self.subs.get(topic, [])):
            h(payload)

# Common topics
TOPIC_PURCHASE_REQ = "purchase_request"     # {customer_id, book_iri, qty}
TOPIC_RESTOCK_REQ  = "restock_request"      # {inventory_iri, qty}
TOPIC_PURCHASE_OK  = "purchase_ok"
TOPIC_PURCHASE_FAIL= "purchase_fail"
