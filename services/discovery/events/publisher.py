import json
from services.discovery.events.envelope import MosaicEvent

class EventPublisher:
    """
    Kafka event publisher abstracting away the underlying client (confluent-kafka).
    If Kafka is unavailable during local development, this provides a loud warning rather than crashing hard if configured to ignore errors.
    """
    def __init__(self, brokers: str = "localhost:9094"):
        self.brokers = brokers
        self.producer = None
        try:
            from confluent_kafka import Producer
            self.producer = Producer({'bootstrap.servers': self.brokers})
        except ImportError:
            print("WARNING: confluent-kafka not installed. Kafka events will not be published.", flush=True)
            
    def publish(self, topic: str, event: MosaicEvent):
        if not self.producer:
            print(f"MOCK PUBLISH to {topic}: {event.model_dump_json()}")
            return
            
        data = event.model_dump_json().encode('utf-8')
        # Use aggregate_id as the partition key for ordering
        self.producer.produce(topic, key=event.aggregate_id.encode('utf-8'), value=data)
        self.producer.poll(0)
        
    def flush(self):
        if self.producer:
            self.producer.flush()
