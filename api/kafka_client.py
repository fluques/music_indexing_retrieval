from aiokafka import AIOKafkaProducer
import asyncio
import json
from music_indexing_retrieval import settings


# Configuration
KAFKA_BOOTSTRAP_SERVERS = [settings.KAFKA_BOOTSTRAP_SERVERS]
KAFKA_TOPIC = settings.KAFKA_TOPIC

async def send_kafka_message(message):
    """Sends a message to the Kafka topic."""
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8') # Serializes to JSON bytes
    )
    await producer.start()
    try:
        await producer.send_and_wait(KAFKA_TOPIC, message)
    finally:
        await producer.stop()
