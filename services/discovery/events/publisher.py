import json
from services.discovery.events.envelope import MosaicEvent

class EventPublisher:
    """
    Kafka event publisher abstracting away the underlying client (confluent-kafka).
    Configurable to raise exceptions on failure, preventing silent failures in real environments.
    """
    def __init__(self, brokers: str = "localhost:9094", raise_on_failure: bool = True):
        self.brokers = brokers
        self.raise_on_failure = raise_on_failure
        self.producer = None
        try:
            from confluent_kafka import Producer
            self.producer = Producer({
                'bootstrap.servers': self.brokers,
                'message.timeout.ms': 5000,
                'socket.timeout.ms': 5000
            })
        except ImportError:
            if self.raise_on_failure:
                raise RuntimeError("confluent-kafka is required but not installed.")
            print("WARNING: confluent-kafka not installed.", flush=True)
            
    def publish(self, topic: str, event: MosaicEvent):
        if not self.producer:
            if self.raise_on_failure:
                raise RuntimeError("Kafka Producer not initialized.")
            print(f"MOCK PUBLISH to {topic}: {event.model_dump_json()}")
            return
            
        data = event.model_dump_json().encode('utf-8')
        
        # Callback to handle delivery failures asynchronously
        def delivery_report(err, msg):
            if err is not None and self.raise_on_failure:
                raise RuntimeError(f"Message delivery failed: {err}")

        try:
            # Use correlation_id (run_id) as the partition key for stable ordering
            self.producer.produce(topic, key=event.correlation_id.encode('utf-8'), value=data, on_delivery=delivery_report)
            self.producer.poll(0)
        except Exception as e:
            if self.raise_on_failure:
                raise RuntimeError(f"Kafka publish failed: {e}")
        
    def flush(self):
        if self.producer:
            # flush returns the number of messages still in queue. 0 means success.
            rem = self.producer.flush(timeout=5.0)
            if rem > 0 and self.raise_on_failure:
                raise RuntimeError(f"Kafka flush failed, {rem} messages remaining.")
